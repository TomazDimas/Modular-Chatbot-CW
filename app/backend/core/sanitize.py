import re

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)

def clean_text(text: str) -> str:
    if not text:
        return text
    text = SCRIPT_RE.sub("", text)
    text = TAG_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
