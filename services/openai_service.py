# services/openai_service.py
from openai import OpenAI
from config import OPENAI_API_KEY

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        # ⚠️ ne PAS passer proxies=... avec le SDK >=1.x
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client

SYSTEM = (
    "Tu es Lanai, compagnon chaleureux pour Mohamed Djeziri (Parkinson). "
    "Phrases courtes, simples, ton rassurant. Pose parfois une petite question douce."
)

def reply_gpt(user_text: str, memory: dict) -> str:
    client = get_client()
    profile = memory.get("profile", {})
    spouse = profile.get("spouse", "Milouda")
    pet = profile.get("pet", "Lana")
    context = f"Contexte: épouse {spouse}, chat {pet}."
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"{context}\nMessage: {user_text}"}
        ],
        max_tokens=140,
        temperature=0.3,
    )
    return r.choices[0].message.content.strip()
