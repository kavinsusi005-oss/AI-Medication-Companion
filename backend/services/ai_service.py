"""
AI Service - Core intelligence layer for MedMate.
Uses Google Gemini API for dynamic language detection, intent understanding,
and natural voice response generation. Falls back to robust rule-based logic when offline.
"""

import os
import json
import re
from google import genai


def get_ai_response(user_message: str, medication_context: str, conversation_history: list = []) -> dict:
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key or api_key == 'your_gemini_api_key_here':
        return get_fallback_response(user_message, medication_context)

    client = genai.Client(api_key=api_key)

    system_prompt = f"""You are a caring medication companion AI for senior citizens named MedMate.

Current medication context: {medication_context}

Your tasks for EVERY user message:
1. Detect the language of the user's message. Return one of: "tamil", "english", "tanglish" (mixed Tamil+English).
2. Detect the user's intent. Return one of:
   - NOT_TAKEN: User says they have NOT taken the medicine (e.g., "I haven't taken it", "didn't take it", "எடுக்கல", "இல்ல")
   - MEDICINE_TAKEN: User says they took the medicine (e.g., "done", "took it", "finished", "எடுத்துட்டேன்", "போட்டுட்டேன்")
   - REMIND_LATER: User wants to be reminded later (e.g., "remind me in 10 min", "பிறகு சொல்லு", "10 minutes later")
   - MEDICATION_QUERY: User asks what medicine to take (e.g., "what medicine?", "என்ன மருந்து?")
   - MEDICATION_INFORMATION_REQUEST: User asks about the purpose of a medicine (e.g., "what is this for?", "எதுக்கு?")
   - GREETING: User greets (e.g., "hello", "vanakkam", "வணக்கம்")
   - CONFIRMATION: User confirms something (e.g., "okay", "சரி")
   - UNKNOWN: Cannot determine intent
3. Generate a warm, caring, simple response in the SAME language as the user's message.
4. For REMIND_LATER intent, extract the number of minutes to delay (default 10 if not specified).

SAFETY RULES (CRITICAL):
- NEVER prescribe, diagnose, or recommend stopping medicines
- NEVER change dosages or suggest alternatives
- NEVER invent medical information
- Only use the medication context provided above
- If asked about something not in the context, say you don't have that information
- Keep responses short and simple for elderly users

Respond ONLY with valid JSON (no markdown, no extra text):
{{"language": "detected_language", "intent": "DETECTED_INTENT", "response": "your response", "delay_minutes": null}}

For REMIND_LATER, set delay_minutes to the extracted number (e.g., 10).
"""

    prompt = f"User says: {user_message}"

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config={
            'system_instruction': system_prompt,
            'temperature': 0.3,
        }
    )

    response_text = response.text

    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        json_str = json_match.group(0) if json_match else response_text

    try:
        parsed = json.loads(json_str)
        return {
            "language": parsed.get("language", "english"),
            "intent": parsed.get("intent", "UNKNOWN"),
            "response": parsed.get("response", "I understand."),
            "delay_minutes": parsed.get("delay_minutes")
        }
    except json.JSONDecodeError:
        return get_fallback_response(user_message, medication_context)


def get_fallback_response(user_message: str, medication_context: str) -> dict:
    msg_lower = user_message.lower()

    has_tamil = any(0x0B80 <= ord(c) <= 0x0BFF for c in user_message)
    has_english = any(c.isalpha() and ord(c) < 128 for c in user_message)
    
    if has_tamil and has_english:
        language = 'tanglish'
    elif has_tamil:
        language = 'tamil'
    else:
        language = 'english'

    is_tamil = has_tamil
    intent = 'UNKNOWN'
    response_text = ''
    delay_minutes = None

    not_taken_words = [
        "haven't", 'not taken', 'havent', 'did not', "didn't", 'not yet', 
        'never', 'no', 'எடுக்கல', 'இல்ல', 'எடுக்கவில்லை', 'இன்னும் எடுக்கல'
    ]
    taken_words = [
        'taken', 'done', 'took', 'finished', 'already took', 'had it',
        'எடுத்த', 'எடுத்துட்டேன்', 'எடுத்தாச்சு', 'சாப்பிட்டேன்', 'போட்டுட்டேன்'
    ]
    remind_words = [
        'remind', 'later', 'minutes', 'min', 'snooze', 'after', 'delay',
        'கழிச்சு', 'நிமிஷம்', 'பிறகு', 'நிமிடம்', 'அப்புறம்'
    ]
    query_words = [
        'what', 'which', 'what is', 'list', 'schedule', 'tablets', 'medicines',
        'என்ன', 'எது', 'எடுக்கணும்', 'மாத்திரை'
    ]
    info_words = [
        'why', 'what for', 'purpose', 'reason', 'use',
        'எதுக்கு', 'ஏன்', 'எதற்கு', 'பயன்'
    ]
    greeting_words = [
        'hello', 'hi', 'hey', 'good morning', 'good evening', 'good afternoon',
        'vanakkam', 'வணக்கம்'
    ]

    if any(w in msg_lower for w in not_taken_words):
        intent = 'NOT_TAKEN'
        if is_tamil:
            response_text = 'சரி. தயவுசெய்து விரைவில் மருந்து எடுத்துக்கொள்ளுங்கள்.'
        else:
            response_text = 'Okay. Please take your medicine as soon as possible.'
    elif any(w in msg_lower for w in taken_words):
        intent = 'MEDICINE_TAKEN'
        if is_tamil:
            response_text = 'நன்றி! உங்கள் மருந்து எடுத்ததாக பதிவு செய்துவிட்டேன்.'
        else:
            response_text = 'Great! Your medication has been recorded as taken.'
    elif any(w in msg_lower for w in remind_words):
        intent = 'REMIND_LATER'
        delay_minutes = 10
        num_match = re.search(r'(\d+)\s*(?:min|minute|நிமிஷ|நிமிட|minutes)', msg_lower)
        if num_match:
            delay_minutes = int(num_match.group(1))
        if is_tamil:
            response_text = f'சரி. {delay_minutes} நிமிடம் கழித்து நினைவூட்டுகிறேன்.'
        else:
            response_text = f'Sure. I will remind you again in {delay_minutes} minutes.'
    elif any(w in msg_lower for w in query_words):
        intent = 'MEDICATION_QUERY'
        if is_tamil:
            response_text = f'உங்கள் தற்போதைய மருந்துகள்: {medication_context}'
        else:
            response_text = f'Your current medications: {medication_context}'
    elif any(w in msg_lower for w in info_words):
        intent = 'MEDICATION_INFORMATION_REQUEST'
        if is_tamil:
            response_text = 'இந்த மருந்து உங்கள் மருத்துவர் பரிந்துரைத்தது. மேலதிக தகவலுக்கு மருத்துவரை அணுகவும்.'
        else:
            response_text = 'This medication was prescribed by your doctor. Please consult your doctor for more information.'
    elif any(w in msg_lower for w in greeting_words):
        intent = 'GREETING'
        if is_tamil:
            response_text = 'வணக்கம்! நான் உங்கள் MedMate மருந்து நினைவூட்டி. எப்படி உதவ முடியும்?'
        else:
            response_text = 'Hello! I am your MedMate companion. How can I help you today?'
    else:
        if is_tamil:
            response_text = 'மன்னிக்கவும், புரியவில்லை. தயவுசெய்து மீண்டும் சொல்லுங்கள்.'
        else:
            response_text = 'Sorry, I did not understand. Could you please say that again?'

    return {
        "language": language,
        "intent": intent,
        "response": response_text,
        "delay_minutes": delay_minutes
    }


def process_message(user_message: str, medication_context: str, conversation_history: list = []) -> dict:
    try:
        return get_ai_response(user_message, medication_context, conversation_history)
    except Exception as e:
        print(f"AI service error (using fallback): {e}")
        return get_fallback_response(user_message, medication_context)
