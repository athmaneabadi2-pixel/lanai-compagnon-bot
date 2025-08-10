# services/openai_service.py
import os
from openai import OpenAI

_CLIENT = None
def _client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _CLIENT

def polish_for_mohamed(profile, raw_text):
    try:
        sys = _persona(profile)
        user = f"Reformule ce texte factuel en 1–2 phrases chaleureuses: {raw_text}"
        r = _client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":sys},{"role":"user","content":user}],
            temperature=0.5, max_tokens=120
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return raw_text

def smalltalk(profile, user_text):
    try:
        sys = _persona(profile)
        r = _client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":sys},
                      {"role":"user","content":f"Message reçu: {user_text}. Réponds en 1–2 phrases max, amical et simple."}],
            temperature=0.6, max_tokens=120
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return "Je suis là si tu veux parler. 💬"
