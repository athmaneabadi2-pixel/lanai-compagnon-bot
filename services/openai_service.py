# services/openai_service.py
import os
from openai import OpenAI

CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _persona(profile: dict) -> str:
    name = profile.get("Identité", {}).get("Prénom", "Mohamed")
    spouse = profile.get("Famille", {}).get("Nom de son épouse", "Milouda")
    pet = "Lana"
    city = profile.get("Identité", {}).get("Ville", "Paris")
    return (
        "Tu es Lanai, compagnon WhatsApp bienveillant. "
        "Style: français, phrases courtes, simples, chaleureuses. "
        f"Parle à {name}. Sa femme: {spouse}. Son chat: {pet}. Ville: {city}. "
        "Jamais de jargon. 1–2 phrases max. Évite les listes. "
        "Si la personne semble fatiguée/stressée: réponse douce, rassurante."
    )

def polish_for_mohamed(profile: dict, raw_text: str) -> str:
    """Reformule un texte factuel en message chaleureux (1–2 phrases)."""
    try:
        sys = _persona(profile)
        user = f"Reformule ce texte factuel pour {profile.get('Identité', {}).get('Prénom','Mohamed')} en 1–2 phrases chaleureuses: {raw_text}"
        r = CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":sys},{"role":"user","content":user}],
            temperature=0.5, max_tokens=120
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return raw_text  # en cas d'erreur, on renvoie la version brute

def smalltalk(profile: dict, user_text: str) -> str:
    """Réponse courte, empathique, type ami."""
    try:
        sys = _persona(profile)
        r = CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":sys},
                {"role":"user","content":f"Message reçu: {user_text}. Réponds en 1–2 phrases max, amical et simple."}
            ],
            temperature=0.6, max_tokens=120
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return "Je suis là si tu veux parler. 💬"

def question_du_jour(profile: dict) -> str:
    """Génère une petite question douce/personnalisée depuis la mémoire JSON."""
    souvenirs = profile.get("Souvenirs", {}) or {}
    theme = souvenirs.get("Thème préféré") or "souvenir agréable"
    try:
        sys = _persona(profile)
        prompt = (f"Propose une seule question courte pour évoquer {theme}. "
                  "1 phrase. Ton chaleureux. Pas de liste.")
        r = CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":sys},{"role":"user","content":prompt}],
            temperature=0.7, max_tokens=80
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return "Et si on parlait d’un bon souvenir aujourd’hui ? 🙂"
