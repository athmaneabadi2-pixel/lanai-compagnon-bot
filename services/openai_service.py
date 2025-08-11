# services/openai_service.py
from openai import OpenAI
import httpx
from config import OPENAI_API_KEY

# Client HTTPX sans proxies, injecté au SDK OpenAI (évite l'erreur 'proxies')
_http_client = httpx.Client(timeout=30.0, follow_redirects=True)

# Client OpenAI v1 — aucun paramètre exotique
client = OpenAI(api_key=OPENAI_API_KEY, http_client=_http_client)

SYSTEM = (
    "Tu es Lanai, compagnon bienveillant pour Mohamed (Parkinson). "
    "Parle en français, tutoie, style simple, phrases courtes, ton chaleureux."
)

def reply_gpt(user_text: str, memory: dict) -> str:
    profile = (memory or {}).get("profile", {})
    mem_str = (
        f"Infos: épouse={profile.get('spouse','Milouda')}, "
        f"enfants={', '.join(profile.get('children', [])) or 'inconnus'}, "
        f"chat={profile.get('pet','Lana')}."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"{mem_str}\n\n{user_text}"},
            ],
            temperature=0.6,
            max_tokens=180,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        # On reste doux et utile côté utilisateur
        return "Désolé, petit bug. On réessaie ? 🙂"
