# HealthMate Chatbot API Documentation

## Overview
This document provides comprehensive API documentation for the HealthMate chatbot system, including both Patient Chatbot and Doctor Chatbot endpoints.

## Base Configuration
- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`
- **Session Header**: `X-Session-ID: unique_session_id`

---

## 1. PATIENT CHATBOT API

### Endpoint: `POST /chatbot`

#### Request Format
```json
{
  "message": "string"
}
```

#### Request Examples

**Start Conversation:**
```json
{
  "message": "I have a headache"
}
```

**Continue Conversation:**
```json
{
  "message": "2 days"
}
```

**Help Command:**
```json
{
  "message": "help"
}
```

**Restart Command:**
```json
{
  "message": "restart"
}
```

**Exit Command:**
```json
{
  "message": "exit"
}
```

#### Response Examples

**1. Initial Greeting:**
```json
{
  "reply_text": "Hello! I'm HealthMate. How are you feeling today?"
}
```

**2. Symptom Collection:**
```json
{
  "reply_text": "Sorry to hear you're dealing with headache. Can I ask, how many days has this been going on?"
}
```

**3. Help Response:**
```json
{
  "reply_text": "🤖 **HealthMate Commands:**\n\n**Conversation Commands:**\n- `help` - Show this help message\n- `restart` or `new` - Start a new conversation\n- `exit`, `quit`, or `stop` - End the conversation\n\n**How to use HealthMate:**\n1. Tell me your symptoms\n2. I'll ask about duration and other details\n3. Get personalized health advice and medication suggestions\n4. Optionally get doctor recommendations\n\n**Example:** \"I have a headache\" or \"I'm feeling feverish\"\n\nType your symptoms to get started! 🏥"
}
```

**4. Medical Advice with Medications:**
```json
{
  "reply_text": "**Summary**\n- Short recap of reported headache, 2 days, and None.\n\nCauses: Possible causes based on headache.\n\n**What you can do**\n- Give 3–4 simple self-care tips based on symptoms headache.\n\nSuggested Medication & Dosage:\n- Paracetamol \n 500mg every 6–8 hours if fever > 100°F \n 2–3 days \n \n\n⚠️ Disclaimer - This chatbot does not provide medical advice. Always consult a doctor before taking or changing any medication. \nIn case of emergency, call your local emergency number.\n\nWould you like me to also suggest some doctors you can consult? (yes/no)",
  "structured": {
    "matched_conditions": ["Common Cold"],
    "medications": [
      {
        "name": "Paracetamol",
        "dosage": "500mg every 6–8 hours if fever > 100°F",
        "duration": "2–3 days",
        "purpose": ""
      }
    ]
  }
}
```

**5. Doctor Recommendations (Clean Response):**
```json
{
  "reply_text": "I found some doctors who specialize in your condition. The recommendations are being displayed in a separate window for your convenience.\n\n==================================================\nWhat would you like to do next?\n- Type 'restart' to start a new consultation\n- Type 'help' to see available commands\n- Type 'exit' to end the conversation",
  "structured": {
    "doctors": [
      {
        "name": "Dr. Smith",
        "qualification": "MD",
        "specialization": ["Cardiology", "Internal Medicine"],
        "contact": "123-456-7890",
        "image": "doctor1.jpg"
      },
      {
        "name": "Dr. Johnson",
        "qualification": "MBBS",
        "specialization": ["General Medicine"],
        "contact": "987-654-3210",
        "image": "doctor2.jpg"
      }
    ]
  }
}
```

**6. Exit Response:**
```json
{
  "reply_text": "Thank you for using HealthMate! Take care and stay healthy! 👋",
  "conversation_ended": true
}
```

---

## 2. DOCTOR CHATBOT API

### Endpoint: `POST /doctor-chatbot`

#### Request Format
```json
{
  "message": "string"
}
```

#### Request Examples

**Start Doctor Consultation:**
```json
{
  "message": "Patient John, 35 years old, complaining of headache and fever"
}
```

**Help Command:**
```json
{
  "message": "help"
}
```

**Restart Command:**
```json
{
  "message": "restart"
}
```

#### Response Examples

**1. Initial Greeting:**
```json
{
  "reply_text": "Hello! I'm Dr. HealthMate AI. Please provide patient information (name, age) and symptoms."
}
```

**2. Medical Assessment with Prescription:**
```json
{
  "reply_text": "**Clinical Assessment:**\nBased on the reported symptoms of headache and fever, this appears to be a case of influenza (flu). The patient presents with typical flu symptoms including headache and elevated body temperature.\n\n**Treatment Plan:**\n- Paracetamol: 500mg every 6-8 hours for fever and pain\n- Oseltamivir: 75mg twice daily for 5 days\n\n**Patient Instructions:**\nTake Paracetamol every 6-8 hours as needed for fever and headache. Start Oseltamivir within 48 hours of symptom onset for best effectiveness. Rest adequately and maintain proper hydration.\n\n**Follow-up:**\nSchedule follow-up in 3-5 days if symptoms persist or worsen. Seek immediate medical attention if breathing difficulties develop.\n\n📋 **Prescription Generated!**\nA downloadable prescription has been created for this patient.\n\nWhat would you like to do next?\n- Type 'restart' to start a new consultation\n- Type 'help' to see available commands\n- Type 'exit' to end the consultation",
  "structured": {
    "matched_conditions": ["Flu"],
    "medications": [
      {
        "name": "Paracetamol",
        "dosage": "500mg every 6-8 hours for fever and pain",
        "duration": "3-5 days",
        "purpose": ""
      },
      {
        "name": "Oseltamivir",
        "dosage": "75mg twice daily",
        "duration": "5 days",
        "purpose": ""
      }
    ],
    "prescription": {
      "prescription_id": "ABC12345",
      "date": "2024-01-15",
      "doctor_name": "Dr. HealthMate AI",
      "patient_info": {
        "name": "John",
        "age": "35"
      },
      "diagnosis": "Flu",
      "medications": [
        {
          "name": "Paracetamol",
          "dosage": "500mg every 6-8 hours for fever and pain",
          "duration": "3-5 days",
          "purpose": ""
        },
        {
          "name": "Oseltamivir",
          "dosage": "75mg twice daily",
          "duration": "5 days",
          "purpose": ""
        }
      ],
      "instructions": "Take Paracetamol every 6-8 hours as needed for fever and headache relief. Start Oseltamivir within 48 hours of symptom onset for optimal effectiveness. Ensure adequate rest and maintain proper hydration throughout treatment.",
      "follow_up": "Schedule a follow-up appointment in 3-5 days if symptoms persist or worsen. Seek immediate medical attention if breathing difficulties, severe dehydration, or high fever (>103°F) develops.",
      "notes": "Patient presents with classic influenza symptoms. Treatment initiated with antiviral therapy and symptomatic relief. Patient counseled on rest and hydration."
    }
  }
}
```

---

## 3. STATUS CHECK APIs

### Patient Chatbot Status: `GET /chatbot/status`

#### Response
```json
{
  "active": true,
  "stage": "ask_duration",
  "has_symptoms": true
}
```

### Doctor Chatbot Status: `GET /doctor-chatbot/status`

#### Response
```json
{
  "active": true,
  "stage": "collect_patient_info",
  "has_patient_info": true,
  "has_symptoms": true
}
```

---

## 4. RESET APIs

### Patient Chatbot Reset: `POST /chatbot/reset`

#### Response
```json
{
  "message": "Conversation reset successfully"
}
```

### Doctor Chatbot Reset: `POST /doctor-chatbot/reset`

#### Response
```json
{
  "message": "Doctor consultation reset successfully"
}
```

---

## 5. PRESCRIPTION DOWNLOAD API

### Endpoint: `GET /prescription/download/{prescription_id}`

#### Response
```json
{
  "message": "Prescription download functionality will be implemented",
  "prescription_id": "ABC12345",
  "note": "This endpoint will generate a downloadable PDF prescription"
}
```

---

## 6. ERROR RESPONSES

### Empty Message Error
```json
{
  "error": "Message cannot be empty"
}
```

### Invalid Session Error
```json
{
  "message": "No active conversation to reset"
}
```

---

## 7. FRONTEND IMPLEMENTATION GUIDE

### Session Management
- Always include `X-Session-ID` header for conversation continuity
- Use unique session IDs for different users/sessions
- Session IDs can be UUIDs or simple strings like "user123"

### Response Handling
- Check for `conversation_ended: true` to know when to end the chat
- Use `structured` data for displaying medications, doctors, or prescriptions
- Handle `reply_text` for chat display
- Check for `error` field for error handling

### Example Frontend Code (JavaScript)

```javascript
// Send message to patient chatbot
const sendMessage = async (message, sessionId) => {
  const response = await fetch('/chatbot', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Session-ID': sessionId
    },
    body: JSON.stringify({ message })
  });
  
  const data = await response.json();
  
  // Display message in chat
  displayMessage(data.reply_text);
  
  // Handle structured data
  if (data.structured) {
    if (data.structured.doctors) {
      showDoctorModal(data.structured.doctors);
    }
    if (data.structured.prescription) {
      showPrescription(data.structured.prescription);
    }
  }
  
  // Check if conversation ended
  if (data.conversation_ended) {
    endChat();
  }
};

// Send message to doctor chatbot
const sendDoctorMessage = async (message, sessionId) => {
  const response = await fetch('/doctor-chatbot', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Session-ID': sessionId
    },
    body: JSON.stringify({ message })
  });
  
  const data = await response.json();
  
  // Display message in chat
  displayMessage(data.reply_text);
  
  // Handle prescription data
  if (data.structured && data.structured.prescription) {
    showPrescriptionModal(data.structured.prescription);
  }
  
  // Check if conversation ended
  if (data.conversation_ended) {
    endChat();
  }
};

// Check conversation status
const checkStatus = async (sessionId, isDoctor = false) => {
  const endpoint = isDoctor ? '/doctor-chatbot/status' : '/chatbot/status';
  const response = await fetch(endpoint, {
    headers: {
      'X-Session-ID': sessionId
    }
  });
  
  return await response.json();
};

// Reset conversation
const resetConversation = async (sessionId, isDoctor = false) => {
  const endpoint = isDoctor ? '/doctor-chatbot/reset' : '/chatbot/reset';
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'X-Session-ID': sessionId
    }
  });
  
  return await response.json();
};
```

### Example Frontend Code (React)

```jsx
import React, { useState, useEffect } from 'react';

const Chatbot = ({ isDoctor = false }) => {
  const [messages, setMessages] = useState([]);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [inputMessage, setInputMessage] = useState('');

  const sendMessage = async (message) => {
    const endpoint = isDoctor ? '/doctor-chatbot' : '/chatbot';
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({ message })
      });
      
      const data = await response.json();
      
      // Add bot response to messages
      setMessages(prev => [...prev, {
        type: 'bot',
        text: data.reply_text,
        structured: data.structured
      }]);
      
      // Handle structured data
      if (data.structured) {
        if (data.structured.doctors) {
          // Show doctor recommendations modal
          showDoctorModal(data.structured.doctors);
        }
        if (data.structured.prescription) {
          // Show prescription modal
          showPrescriptionModal(data.structured.prescription);
        }
      }
      
      // Check if conversation ended
      if (data.conversation_ended) {
        // Handle conversation end
        handleConversationEnd();
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      // Add user message to chat
      setMessages(prev => [...prev, {
        type: 'user',
        text: inputMessage
      }]);
      
      // Send to chatbot
      sendMessage(inputMessage);
      
      // Clear input
      setInputMessage('');
    }
  };

  return (
    <div className="chatbot-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <div className="text">{msg.text}</div>
            {msg.structured && (
              <div className="structured-data">
                {/* Handle structured data display */}
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type your message..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default Chatbot;
```

---

## 8. TESTING EXAMPLES

### Using curl

```bash
# Test patient chatbot
curl -X POST http://localhost:5000/chatbot \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: test123" \
  -d '{"message": "I have a headache"}'

# Test doctor chatbot
curl -X POST http://localhost:5000/doctor-chatbot \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: doctor123" \
  -d '{"message": "Patient John, 35 years old, complaining of headache and fever"}'

# Check status
curl -X GET http://localhost:5000/chatbot/status \
  -H "X-Session-ID: test123"
```

### Using JavaScript fetch

```javascript
// Test patient chatbot
fetch('http://localhost:5000/chatbot', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Session-ID': 'test123'
  },
  body: JSON.stringify({ message: 'I have a headache' })
})
.then(response => response.json())
.then(data => console.log(data));

// Test doctor chatbot
fetch('http://localhost:5000/doctor-chatbot', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Session-ID': 'doctor123'
  },
  body: JSON.stringify({ message: 'Patient John, 35 years old, complaining of headache and fever' })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 9. COMMON USE CASES

### Patient Chatbot Flow
1. User starts conversation with symptoms
2. Bot asks for duration and other details
3. Bot provides medical advice and medication suggestions
4. Bot offers doctor recommendations
5. User can restart or exit

### Doctor Chatbot Flow
1. Doctor provides patient information and symptoms
2. Bot generates medical assessment
3. Bot creates prescription with medications
4. Prescription is available for download
5. Doctor can restart or exit

---

## 10. NOTES FOR FRONTEND DEVELOPER

- **Session Management**: Always use the same `X-Session-ID` for a conversation
- **Error Handling**: Check for `error` field in responses
- **Structured Data**: Use `structured` field for medications, doctors, prescriptions
- **Conversation End**: Check `conversation_ended` flag to handle chat termination
- **Real-time Updates**: Consider WebSocket implementation for real-time chat
- **Mobile Responsive**: Ensure chat interface works on mobile devices
- **Accessibility**: Add proper ARIA labels and keyboard navigation

---

This documentation provides everything needed to integrate with both chatbot APIs. For any questions or clarifications, please refer to the test files or contact the backend team.
