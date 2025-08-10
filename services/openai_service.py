import os
from openai import OpenAI
from config import OPENAI_API_KEY

# ❌ NE PAS passer proxies=...
# ✅ Version correcte pour le SDK v1
client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM = "Tu es Lanai, compagnon bienveillant. Langage simple, phrases courtes. Toujours chaleureux."

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
        return "Désolé, je bug un peu. On réessaie ?"
