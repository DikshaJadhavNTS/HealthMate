
import os
import json
import random
from typing import List, Dict, Any, Optional
from openai import OpenAI
from rapidfuzz import fuzz

# ---- Configuration ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = "gpt-4o-mini"
client = OpenAI(api_key=OPENAI_API_KEY)

# ---- Load Data ----
with open("new.json", "r", encoding="utf-8") as f:
    med_data = json.load(f)

with open("doctor.json", "r", encoding="utf-8") as f:
    doctor_data = json.load(f)

with open("condition_specialization.json", "r", encoding="utf-8") as f:
    condition_specialization = json.load(f)

# ---- Utilities ----
def _normalize(text: str) -> str:
    return (text or "").strip().lower()

def is_smalltalk(user_text: str) -> Optional[str]:
    """Detect small talk and respond naturally."""
    t = _normalize(user_text)
    if any(greet in t for greet in ["hi", "hello", "hey"]):
        return "Hi there! How are you feeling today?"
    if "how are you" in t:
        return "I’m doing great, thank you! More importantly, how are you feeling?"
    if "not feeling well" in t:
        return "I’m sorry to hear that. Can you tell me more about your symptoms?"
    return None

# ---- Symptom & Doctor Matching ----
def match_symptoms(user_input: str, threshold: int = 60) -> List[str]:
    """Match free-text input to known conditions/symptoms using fuzzy match."""
    u = _normalize(user_input)
    symptom_to_condition = {}
    for condition, info in med_data.items():
        symptom_to_condition[condition.lower()] = condition
        for symptom in info.get("symptoms", []):
            symptom_to_condition[symptom.lower()] = condition

    matched = set()
    for symptom_text, condition in symptom_to_condition.items():
        score = fuzz.token_set_ratio(symptom_text, u)
        if score >= threshold:
            matched.add(condition)
    return list(matched)

def match_doctors_by_condition(conditions: List[str], top_n: int = 4) -> List[Dict[str, Any]]:
    """Find doctors based on condition_specialization mapping."""
    matched = []
    for cond in conditions:
        specializations = condition_specialization.get(cond, [])
        for spec in specializations:
            for doc in doctor_data:
                if spec in doc.get("specialization", []):
                    if doc not in matched:
                        matched.append(doc)
    return matched[:top_n]

# ---- Medication Helper ----
def build_med_list(meds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    dedup = {}
    for m in meds:
        key = m.get("name", "").strip().lower()
        if not key:
            continue
        if key not in dedup:
            dedup[key] = {
                "name": m.get("name"),
                "dosage": m.get("dosage", "As directed"),
                "duration": m.get("duration", ""),
                "purpose": m.get("purpose", "")
            }
    return list(dedup.values())

# ---- AI Response Builder ----
def build_prompt_plaintext(symptoms_text: str,
                           matched_conditions: List[str],
                           other_symptoms: str,
                           duration: str,
                           allergies: str,
                           meds_for_conditions: List[Dict[str, Any]]) -> str:
    meds_list_text = "\n".join(
        [f"- {m['name']} \n {m['dosage']} \n {m.get('duration','')} \n {m.get('purpose','')}"
         for m in build_med_list(meds_for_conditions)]
    ) or "- No medication suggestion available"

    prompt = f"""
You are HealthMate, a warm, friendly, safety-first medical assistant.
Assist the patient based on their symptoms: {symptoms_text}, duration: {duration}, and other symptoms: {other_symptoms}.
Create a plain-text patient-facing response in this structure:

*Summary*
- Short recap of reported {symptoms_text}, {duration}, and {other_symptoms}.

Causes: Possible causes based on {symptoms_text}.

*What you can do*
- Give 3–4 simple self-care tips based on symptoms {symptoms_text}.

Suggested Medication & Dosage:
{meds_list_text}

Always finish with:
"⚠️ Disclaimer - This chatbot does not provide medical advice. Always consult a doctor before taking or changing any medication. 
In case of emergency, call your local emergency number."
"""
    return prompt.strip()

def generate_plaintext_response(symptoms_text: str,
                                matched_conditions: List[str],
                                other_symptoms: str,
                                duration: str,
                                allergies: str,
                                meds_for_conditions: List[Dict[str, Any]]) -> str:
    prompt = build_prompt_plaintext(
        symptoms_text=symptoms_text,
        matched_conditions=matched_conditions,
        other_symptoms=other_symptoms or "None",
        duration=duration or "Not specified",
        allergies=allergies or "None",
        meds_for_conditions=meds_for_conditions
    )
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful, safe, conversational medical assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

# ---- Conversation Manager ----
class ConversationManager:
    def __init__(self):
        self.stage = "greeting"
        self.symptoms = ""
        self.duration = ""
        self.other_symptoms = ""
        self.allergies = ""
        self.matched_conditions = []

    def _choose(self, options):
        return random.choice(options)

    def process(self, user_text: str) -> Dict[str, Any]:
        user_text = user_text.strip().lower()

        # Stage 1: greeting
        if self.stage == "greeting":
            self.stage = "ask_symptoms"
            return {"reply_text": self._choose([
                "Hello! I'm HealthMate. How are you feeling today?",
                "Hi there, I’m HealthMate. Tell me what symptoms are bothering you.",
                "Hey! I’m here to help. Could you share your symptoms with me?"
            ])}

        # Stage 2: symptoms
        if self.stage == "ask_symptoms":
            self.symptoms = user_text
            self.matched_conditions = match_symptoms(user_text)
            self.stage = "ask_duration"
            return {"reply_text": self._choose([
                f"Sorry to hear you’re dealing with {user_text}. Can I ask, how many days has this been going on?",
                f"Got it. You mentioned {user_text}. Since when are you feeling this way?",
                f"Thanks for sharing. To understand better, how long have you had these symptoms?"
            ])}

        # Stage 3: duration
        if self.stage == "ask_duration":
            self.duration = user_text
            self.stage = "ask_other"
            return {"reply_text": self._choose([
                "Okay, noted. Do you have any other symptoms along with this?",
                "Thanks. Are you noticing anything else unusual in your health?",
                "Got it. Apart from this, any other symptoms?"
            ])}

        # Stage 4: other symptoms
        if self.stage == "ask_other":
            self.other_symptoms = user_text
            self.stage = "ask_allergies"
            return {"reply_text": self._choose([
                "Thanks for telling me. Do you have any allergies or dietary concerns?",
                "Okay. Just to be safe, do you have any known allergies?",
                "Got it. Do you have any allergies to medicines or food?"
            ])}

        # Stage 5: allergies
        if self.stage == "ask_allergies":
            self.allergies = user_text
            self.stage = "give_advice"

            if not self.matched_conditions:
                return {
                    "reply_text": self._choose([
                        "Hmm, I couldn’t clearly match your symptoms. It might be best to check with a doctor.",
                        "Sorry, I don’t have enough info to suggest medicines safely. Please consult a doctor."
                    ]),
                    "structured": {"matched_conditions": []}
                }

            aggregated_meds = []
            for cond in self.matched_conditions:
                aggregated_meds.extend(med_data.get(cond, {}).get("medications", []))

            ai_summary = generate_plaintext_response(
                symptoms_text=self.symptoms,
                matched_conditions=self.matched_conditions,
                other_symptoms=self.other_symptoms,
                duration=self.duration,
                allergies=self.allergies,
                meds_for_conditions=aggregated_meds
            )

            reply = (
                f"{ai_summary}\n\n"
                "Would you like me to also suggest some doctors you can consult? (yes/no)"
            )
            return {
                "reply_text": reply,
                "structured": {
                    "matched_conditions": self.matched_conditions,
                    "medications": build_med_list(aggregated_meds)
                }
            }

        # Stage 6: doctor recommendation
        if self.stage == "give_advice":
            if user_text in ["yes", "y"]:
                docs = match_doctors_by_condition(self.matched_conditions)
                if not docs:
                    return {"reply_text": "Sorry, I couldn’t find doctors for your case right now."}

                lines = ["Doctor Recommendation Based on symptoms:"]
                for i, doc in enumerate(docs, 1):
                    lines.append(
                        f"{i}. {doc['name']} ({doc['qualification']}) – {', '.join(doc['specialization'])}\n"
                        f"   Contact: {doc['contact']}\n"
                        f"   Image: {doc.get('image', 'No image available')}"
                    )
                return {"reply_text": "\n".join(lines), "structured": {"doctors": docs}}

            elif user_text in ["no", "n"]:
                return {"reply_text": self._choose([
                    "Alright, please rest and take care. Let me know if you need more help.",
                    "Okay. Stay safe and get well soon.",
                    "No problem. I’m here if you want advice later."
                ])}

            else:
                return {"reply_text": "Please reply with 'yes' or 'no'."}

        return {"reply_text": "I didn’t quite get that. Can you rephrase?"}

def handle_user_interaction(user_input_text: str,
                            duration: Optional[str] = None,
                            other_symptoms: Optional[str] = None,
                            allergies: Optional[str] = None,
                            mode: str = "text",
                            want_doctors: bool = True) -> Dict[str, Any]:
    st_response = is_smalltalk(user_input_text)
    if st_response:
        return {"reply_text": st_response, "structured": {"matched_conditions": []}}

    matched_conditions = match_symptoms(user_input_text)
    if not matched_conditions:
        return {
            "reply_text": "Sorry, I couldn't find a recommended medicine. Please consult a doctor.",
            "structured": {"matched_conditions": []}
        }

    aggregated_meds = []
    for cond in matched_conditions:
        aggregated_meds.extend(med_data.get(cond, {}).get("medications", []))

    ai_text = generate_plaintext_response(
        symptoms_text=user_input_text,
        matched_conditions=matched_conditions,
        other_symptoms=other_symptoms or "",
        duration=duration or "",
        allergies=allergies or "",
        meds_for_conditions=aggregated_meds
    )

    doctors = []
    if want_doctors:
        doctors = match_doctors_by_condition(matched_conditions)

    structured = {
        "matched_conditions": matched_conditions,
        "summary": f"{', '.join(set(matched_conditions))} — reported for {duration or 'N/A'}",
        "medications": build_med_list(aggregated_meds),
        "doctors": doctors,
        "ai_text": ai_text
    }

    if mode == "json":
        return {"reply_text": ai_text, "structured": structured}
    else:
        return {"reply_text": ai_text}