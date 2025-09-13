import os
import json
import random
from typing import List, Dict, Any, Optional
from openai import OpenAI
from rapidfuzz import fuzz
from datetime import datetime, date
import uuid

# ---- Configuration ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = "gpt-4o-mini"
client = OpenAI(api_key=OPENAI_API_KEY)

# ---- Load Data ----
with open("new.json", "r", encoding="utf-8") as f:
    med_data = json.load(f)

with open("doctor.json", "r", encoding="utf-8") as f:
    doctor_data = json.load(f)

# ---- Utilities ----
def _normalize(text: str) -> str:
    return (text or "").strip().lower()

def is_smalltalk(user_text: str) -> Optional[str]:
    """Detect small talk and respond professionally."""
    t = _normalize(user_text)
    if any(greet in t for greet in ["hi", "hello", "hey"]):
        return "Hello! I'm Dr. HealthMate AI. How can I assist you with your medical consultation today?"
    if "how are you" in t:
        return "I'm doing great, thank you. How are you feeling today? What symptoms are you experiencing?"
    if "thank you" in t or "thanks" in t:
        return "You're welcome! Is there anything else I can help you with regarding your health?"
    return None

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

def build_med_list(meds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build and deduplicate medication list."""
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

# ---- Prescription Generator ----
def generate_prescription(patient_info: Dict[str, Any], 
                         diagnosis: str, 
                         medications: List[Dict[str, Any]], 
                         doctor_name: str = "Dr. HealthMate AI") -> Dict[str, Any]:
    """Generate a structured prescription."""
    prescription_id = str(uuid.uuid4())[:8].upper()
    current_date = date.today().strftime("%Y-%m-%d")
    
    prescription = {
        "prescription_id": prescription_id,
        "date": current_date,
        "doctor_name": doctor_name,
        "patient_info": patient_info,
        "diagnosis": diagnosis,
        "medications": medications,
        "instructions": generate_medication_instructions(medications),
        "follow_up": generate_follow_up_instructions(diagnosis),
        "notes": generate_prescription_notes(patient_info, diagnosis)
    }
    
    return prescription

def generate_medication_instructions(medications: List[Dict[str, Any]]) -> str:
    """Generate medication instructions using AI."""
    med_list = "\n".join([f"- {m['name']}: {m['dosage']} for {m['duration']}" for m in medications])
    
    prompt = f"""
    As a medical professional, provide clear medication instructions for these medications:
    {med_list}
    
    Include:
    - When to take each medication
    - Important warnings or side effects to watch for
    - What to do if symptoms worsen
    - General medication safety tips
    
    Keep instructions clear and professional.
    """
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a professional doctor providing medication instructions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def generate_follow_up_instructions(diagnosis: str) -> str:
    """Generate follow-up instructions using AI."""
    prompt = f"""
    As a doctor, provide follow-up instructions for a patient diagnosed with: {diagnosis}
    
    Include:
    - When to schedule follow-up appointment
    - Warning signs that require immediate medical attention
    - General health recommendations
    - When to contact the doctor
    
    Keep instructions clear and professional.
    """
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a professional doctor providing follow-up care instructions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=250
    )
    return response.choices[0].message.content.strip()

def generate_prescription_notes(patient_info: Dict[str, Any], diagnosis: str) -> str:
    """Generate prescription notes using AI."""
    patient_summary = f"Patient: {patient_info.get('name', 'Unknown')}, Age: {patient_info.get('age', 'Not specified')}"
    
    prompt = f"""
    As a doctor, write brief clinical notes for this prescription:
    Patient: {patient_summary}
    Diagnosis: {diagnosis}
    
    Include:
    - Brief clinical assessment
    - Treatment rationale
    - Any special considerations
    
    Keep it professional and concise.
    """
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a professional doctor writing clinical notes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# ---- AI Response Builder ----
def build_doctor_prompt(patient_symptoms: str,
                       matched_conditions: List[str],
                       patient_info: Dict[str, Any],
                       medications: List[Dict[str, Any]]) -> str:
    """Build prompt for doctor AI response."""
    
    patient_summary = f"Patient: {patient_info.get('name', 'Unknown')}, Age: {patient_info.get('age', 'Not specified')}"
    med_list_text = "\n".join(
        [f"- {m['name']}: {m['dosage']} for {m.get('duration','')}" for m in medications]
    ) or "- No medication recommendation available"

    prompt = f"""
    You are Dr. HealthMate AI, a professional medical assistant helping doctors provide patient care.
    
    Patient Information: {patient_summary}
    Reported Symptoms: {patient_symptoms}
    Likely Conditions: {', '.join(matched_conditions)}
    
    Provide a professional medical response in this structure:
    
    **Clinical Assessment:**
    - Brief assessment of the reported symptoms
    - Likely diagnosis based on symptoms
    
    **Treatment Plan:**
    - Recommended medications and dosages
    {med_list_text}
    
    **Patient Instructions:**
    - How to take medications
    - Lifestyle recommendations
    - Warning signs to watch for
    
    **Follow-up:**
    - When to return for follow-up
    - Emergency situations requiring immediate care
    
    Always maintain professional medical language and include appropriate disclaimers.
    """
    return prompt.strip()

def generate_doctor_response(patient_symptoms: str,
                           matched_conditions: List[str],
                           patient_info: Dict[str, Any],
                           medications: List[Dict[str, Any]]) -> str:
    """Generate doctor AI response."""
    prompt = build_doctor_prompt(
        patient_symptoms=patient_symptoms,
        matched_conditions=matched_conditions,
        patient_info=patient_info,
        medications=medications
    )
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are Dr. HealthMate AI, a professional medical assistant. Provide clear, professional medical advice."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

# ---- Doctor Conversation Manager ----
class DoctorConversationManager:
    def __init__(self):
        self.reset_conversation()

    def reset_conversation(self):
        """Reset the conversation to start fresh"""
        self.stage = "greeting"
        self.patient_info = {}
        self.symptoms = ""
        self.matched_conditions = []
        self.conversation_active = True

    def _choose(self, options):
        return random.choice(options)

    def _is_exit_command(self, text: str) -> bool:
        """Check if user wants to exit/stop the conversation"""
        exit_words = ["exit", "quit", "stop", "bye", "goodbye", "end", "close"]
        return text in exit_words

    def _is_restart_command(self, text: str) -> bool:
        """Check if user wants to restart/start new conversation"""
        restart_words = ["restart", "new", "start over", "begin again", "reset"]
        return text in restart_words

    def _is_help_command(self, text: str) -> bool:
        """Check if user wants help"""
        help_words = ["help", "commands", "what can you do", "options"]
        return text in help_words

    def _get_help_message(self) -> str:
        """Return help message with available commands"""
        return """🩺 **Dr. HealthMate AI Commands:**
        
**Conversation Commands:**
- `help` - Show this help message
- `restart` or `new` - Start a new consultation
- `exit`, `quit`, or `stop` - End the consultation

**How to use Dr. HealthMate AI:**
1. Provide patient information (name, age)
2. Describe the patient's symptoms
3. Get AI-powered medical assessment
4. Generate downloadable prescription
5. Provide follow-up instructions

**Example:** "Patient John, 35 years old, complaining of headache and fever"

Type patient information to start a consultation! 🏥"""

    def process(self, user_text: str) -> Dict[str, Any]:
        user_text = user_text.strip().lower()

        # Check for special commands first
        if self._is_help_command(user_text):
            return {"reply_text": self._get_help_message()}
        
        if self._is_exit_command(user_text):
            self.conversation_active = False
            return {"reply_text": self._choose([
                "Consultation ended. Thank you for using Dr. HealthMate AI! 👋",
                "Session complete. Dr. HealthMate AI is always available for medical consultations. 👋",
                "Consultation finished. Take care and stay healthy! 👋"
            ]), "conversation_ended": True}
        
        if self._is_restart_command(user_text):
            self.reset_conversation()
            return {"reply_text": self._choose([
                " New consultation started! Hello, I'm Dr. HealthMate AI. Please provide patient information.",
                " Fresh consultation! I'm Dr. HealthMate AI. What patient information can you provide?",
                " Ready for new consultation! I'm Dr. HealthMate AI. Please share patient details."
            ])}

        # Stage 1: greeting
        if self.stage == "greeting":
            self.stage = "collect_patient_info"
            return {"reply_text": self._choose([
                "Hello! I'm Dr. HealthMate AI. Please provide patient information (name, age) and symptoms.",
                "Welcome! I'm Dr. HealthMate AI. What patient information and symptoms can you share?",
                "Good day! I'm Dr. HealthMate AI. Please provide patient details and their symptoms."
            ])}

        # Stage 2: collect patient info and symptoms
        if self.stage == "collect_patient_info":
            # Try to extract patient info and symptoms from the input
            self.symptoms = user_text
            
            # Simple extraction (can be enhanced with NLP)
            words = user_text.split()
            if "years" in user_text or "old" in user_text:
                # Try to extract age
                for i, word in enumerate(words):
                    if word.isdigit() and i + 1 < len(words) and words[i + 1] in ["years", "old"]:
                        self.patient_info["age"] = word
                        break
            
            # Extract name (simple approach - first word if it's capitalized)
            first_word = user_text.split()[0] if user_text.split() else ""
            if first_word and first_word[0].isupper():
                self.patient_info["name"] = first_word
            
            self.matched_conditions = match_symptoms(user_text)
            self.stage = "provide_assessment"

            if not self.matched_conditions:
                return {
                    "reply_text": "I couldn't clearly identify a specific condition from the symptoms. Could you provide more detailed symptom information?",
                    "structured": {"matched_conditions": []}
                }

            # Generate medications for matched conditions
            aggregated_meds = []
            for cond in self.matched_conditions:
                aggregated_meds.extend(med_data.get(cond, {}).get("medications", []))

            # Generate doctor response
            doctor_response = generate_doctor_response(
                patient_symptoms=self.symptoms,
                matched_conditions=self.matched_conditions,
                patient_info=self.patient_info,
                medications=aggregated_meds
            )

            # Generate prescription
            prescription = generate_prescription(
                patient_info=self.patient_info,
                diagnosis=", ".join(self.matched_conditions),
                medications=build_med_list(aggregated_meds),
                doctor_name="Dr. HealthMate AI"
            )

            reply = (
                f"{doctor_response}\n\n"
                " **Prescription Generated!**\n"
                "A downloadable prescription has been created for this patient.\n\n"
                "What would you like to do next?\n"
                "- Type 'restart' to start a new consultation\n"
                "- Type 'help' to see available commands\n"
                "- Type 'exit' to end the consultation"
            )
            
            return {
                "reply_text": reply,
                "structured": {
                    "matched_conditions": self.matched_conditions,
                    "medications": build_med_list(aggregated_meds),
                    "prescription": prescription
                }
            }

        return {"reply_text": "I didn't quite get that. Can you rephrase? Type 'help' to see available commands."}

# ---- Main Function for Direct Use ----
def handle_doctor_consultation(user_input_text: str,
                              patient_info: Optional[Dict[str, Any]] = None,
                              mode: str = "text") -> Dict[str, Any]:
    """Handle doctor consultation directly."""
    st_response = is_smalltalk(user_input_text)
    if st_response:
        return {"reply_text": st_response, "structured": {"matched_conditions": []}}

    matched_conditions = match_symptoms(user_input_text)
    if not matched_conditions:
        return {
            "reply_text": "I couldn't identify a specific condition. Please provide more detailed symptom information.",
            "structured": {"matched_conditions": []}
        }

    # Generate medications
    aggregated_meds = []
    for cond in matched_conditions:
        aggregated_meds.extend(med_data.get(cond, {}).get("medications", []))

    # Generate doctor response
    doctor_response = generate_doctor_response(
        patient_symptoms=user_input_text,
        matched_conditions=matched_conditions,
        patient_info=patient_info or {},
        medications=aggregated_meds
    )

    # Generate prescription
    prescription = generate_prescription(
        patient_info=patient_info or {},
        diagnosis=", ".join(matched_conditions),
        medications=build_med_list(aggregated_meds),
        doctor_name="Dr. HealthMate AI"
    )

    structured = {
        "matched_conditions": matched_conditions,
        "medications": build_med_list(aggregated_meds),
        "prescription": prescription,
        "doctor_response": doctor_response
    }

    if mode == "json":
        return {"reply_text": doctor_response, "structured": structured}
    else:
        return {"reply_text": doctor_response}
