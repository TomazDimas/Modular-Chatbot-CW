from __future__ import annotations
import re


MATH_ONLY_REGEX = re.compile(r"^\s*[\d\.\s\+\-\*\/\(\)]+\s*$")

INJECTION_PATTERNS = [
    r"(?i)ignore (previous|all) instructions",
    r"(?i)system prompt",
    r"(?i)developer mode",
    r"(?i)prompt injection",
]

def sanitize_minimal(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return " ".join(text.split()).strip()

def seems_injection(text: str) -> bool:
    return any(re.search(p, text or "") for p in INJECTION_PATTERNS)
