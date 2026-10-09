def detect_language(text: str) -> str:
    has_tamil = any(0x0B80 <= ord(c) <= 0x0BFF for c in text)
    has_english = any(c.isalpha() and ord(c) < 128 for c in text)
    if has_tamil and has_english:
        return 'tanglish'
    elif has_tamil:
        return 'tamil'
    return 'english'
