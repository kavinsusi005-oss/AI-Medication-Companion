def detect_intent_simple(text: str) -> str:
    msg_lower = text.lower()
    
    # 1. Check NOT_TAKEN first
    not_taken_words = [
        "haven't", 'not taken', 'havent', 'did not', "didn't", 'not yet', 
        'never', 'no', 'எடுக்கல', 'இல்ல', 'எடுக்கவில்லை', 'இன்னும் எடுக்கல'
    ]
    if any(w in msg_lower for w in not_taken_words):
        return 'NOT_TAKEN'
        
    # 2. Check MEDICINE_TAKEN
    taken_words = [
        'taken', 'done', 'took', 'finished', 'already took', 'had it',
        'எடுத்த', 'எடுத்துட்டேன்', 'எடுத்தாச்சு', 'சாப்பிட்டேன்', 'போட்டுட்டேன்'
    ]
    if any(w in msg_lower for w in taken_words):
        return 'MEDICINE_TAKEN'
        
    # 3. Check REMIND_LATER
    remind_words = [
        'remind', 'later', 'minutes', 'min', 'snooze', 'after', 'delay',
        'கழிச்சு', 'நிமிஷம்', 'பிறகு', 'நிமிடம்', 'அப்புறம்'
    ]
    if any(w in msg_lower for w in remind_words):
        return 'REMIND_LATER'
        
    # 4. Check MEDICATION_QUERY
    query_words = [
        'what', 'which', 'what is', 'list', 'schedule', 'tablets', 'medicines',
        'என்ன', 'எது', 'எடுக்கணும்', 'மாத்திரை'
    ]
    if any(w in msg_lower for w in query_words):
        return 'MEDICATION_QUERY'
        
    # 5. Check MEDICATION_INFORMATION_REQUEST
    info_words = [
        'why', 'what for', 'purpose', 'reason', 'use',
        'எதுக்கு', 'ஏன்', 'எதற்கு', 'பயன்'
    ]
    if any(w in msg_lower for w in info_words):
        return 'MEDICATION_INFORMATION_REQUEST'
        
    # 6. Check GREETING
    greeting_words = [
        'hello', 'hi', 'hey', 'good morning', 'good evening', 'good afternoon',
        'vanakkam', 'வணக்கம்'
    ]
    if any(w in msg_lower for w in greeting_words):
        return 'GREETING'
        
    return 'UNKNOWN'
