import re

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_valid_speech_input(text: str) -> bool:
    if not text or not text.strip():
        return False
    cleaned = clean_text(text)
    if re.fullmatch(r'[\W_]+', cleaned):
        return False
    return len(cleaned) > 0
