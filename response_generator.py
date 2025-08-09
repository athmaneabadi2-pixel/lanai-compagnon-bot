# response_generator.py
import os
import re
import unicodedata
import requests
from openai import OpenAI
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

client_ai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

API_FOOT_KEY = os.environ.get("API_FOOT_KEY")
BASE_URL = "https://v3.football.api-sports.io"

# Aliases -> (team_id, canonical_name)
TEAM_ALIASES = {
    # PSG
    "psg": (85, "PSG"),
    "paris sg": (85, "PSG"),
    "paris": (85, "PSG"),
    "paris saint-germain": (85, "PSG"),
    # OM
    "om": (81, "OM"),
    "marseille": (81, "OM"),
    "olympique de marseille": (81, "OM"),
    # Lyon
    "lyon": (80, "Lyon"),
    "ol": (80, "Lyon"),
    "olympique lyonnais": (80, "Lyon"),
    # RC Lens
    "rc lens": (116, "RC Lens"),
    "lens": (116, "RC Lens"),
    # Monaco
    "monaco": (91, "Monaco"),
    "asm": (91, "Monaco"),
}

def _slug(txt: str) -> str:
    if not txt:
        return ""
    txt = txt.lower().strip()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = re.sub(r"\s+", " ", txt)
    return txt

def guess_team_from_text(message: str):
    """Essaye d’inférer l’équipe depuis le texte utilisateur."""
    s = _slug(message)
    # correspondance exacte
    if s in TEAM_ALIASES:
        return TEAM_ALIASES[s]
    # correspondance partielle
    for alias, (tid, canon) in TEAM_ALIASES.items():
        if alias in s:
            return tid, canon
    return None, None

def get_next_match(team_name: str) -> str:
    if not API_FOOT_KEY:
        return "La clé API foot est manquante côté serveur."
    # trouver l’ID via les alias
    tid, canon = guess_team_from_text(team_name)
    if not tid:
        # si team_name vient déjà propre de l’intent, on tente quand même
        tid, canon = guess_team_from_text(canon or team_name)
    if not tid:
        return f"Désolé, je ne trouve pas l'équipe « {team_name} ». Essaie : RC Lens, PSG, OM, Lyon, Monaco."

    url = f"{BASE_URL}/fixtures?team={tid}&next=1"
    headers = {"x-apisports-key": API_FOOT_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=12)
    except Exception:
        return "Le service des matchs ne répond pas pour le moment."

    if r.status_code != 200:
        return "Impossible de récupérer le prochain match pour cette équipe."

    data = r.json()
    if not data.get("response"):
        return f"Pas de prochain match trouvé pour {canon}."
    match = data["response"][0]
    date_iso = match["fixture"]["date"]  # ex: 2025-08-15T19:00:00+00:00
    # on formate en heure Paris si possible
    try:
        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Paris"))
        date_str = dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        date_str = date_iso[:10]

    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]
    return f"Prochain match de {canon} : {home} vs {away}, le {date_str}."

def generate_gpt_response(user_msg: str, data_json: dict) -> str:
    prompt = (
        "Tu es Lanai, un compagnon bienveillant pour Mohamed Djeziri. "
        "Tu parles simplement, en phrases courtes, sans jargon. "
        "Sa femme s'appelle Milouda, son chat Lana. "
        "Pour la santé: conseils généraux uniquement, sans diagnostic. "
        f"Contexte: {data_json}\n"
        f"Message: « {user_msg} »"
    )
    resp = client_ai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()

def generate_response(intent: dict, user_msg: str, data_json: dict) -> str:
    text = user_msg.lower()

    # Petit handler pour la date du jour (évite que GPT invente une date)
    if "quelle date" in text or "quel jour" in text or "date d'aujourd" in text:
        try:
            today = datetime.now(ZoneInfo("Europe/Paris")).strftime("%A %d %B %Y").capitalize()
        except Exception:
            today = datetime.now().strftime("%A %d %B %Y").capitalize()
        return f"Aujourd’hui, nous sommes le {today}."

    # ======= FOOT =======
    if intent.get("intent") == "football":
        action = (intent.get("action") or "").lower()
        team = intent.get("team")

        # si le détecteur n'a pas mis l'équipe, on essaie de l'inférer du texte
        if not team:
            _, maybe = guess_team_from_text(user_msg)
            if maybe:
                team = maybe

        # heuristique si on parle de match sans action explicite
        if not action and any(k in text for k in ["match", "prochain", "joue quand", "calendrier"]):
            action = "next_match"

        if action == "next_match" and team:
            return get_next_match(team)

        return "Tu veux parler de foot ? Dis-moi l’équipe (ex : RC Lens, PSG, OM) et ce que tu veux (prochain match, score, calendrier)."

    # ======= BASKET (placeholder pour l’instant) =======
    if intent.get("intent") == "basketball":
        return "Pour le basket (NBA), je pourrai bientôt te donner les prochains matchs. Dis-moi l’équipe (ex : Lakers, Celtics)."

    # ======= MÉTÉO (placeholder) =======
    if intent.get("intent") == "weather":
        return "Pour la météo, dis-moi la ville et le jour (ex : Paris demain)."

    # ======= GPT compagnon (fallback) =======
    return generate_gpt_response(user_msg, data_json)
