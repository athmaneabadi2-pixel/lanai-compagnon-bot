# response_generator.py
import os
import re
import unicodedata
import requests
from openai import OpenAI

client_ai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

API_FOOT_KEY = os.environ.get("API_FOOT_KEY")
BASE_URL = "https://v3.football.api-sports.io"

# Aliases simples -> IDs API-Football (à compléter selon besoin)
TEAM_IDS = {
    "psg": 85, "paris sg": 85, "paris": 85,
    "om": 81, "marseille": 81,
    "lyon": 80, "ol": 80, "olympique lyonnais": 80,
    "rc lens": 116, "lens": 116,
    "monaco": 91, "asm": 91,
}

def _slug(txt: str) -> str:
    if not txt:
        return ""
    txt = txt.lower().strip()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = re.sub(r"\s+", " ", txt)
    return txt

def _resolve_team_id(team_name: str):
    key = _slug(team_name)
    if key in TEAM_IDS:
        return TEAM_IDS[key]
    for alias, tid in TEAM_IDS.items():
        if alias in key:
            return tid
    return None

def get_next_match(team_name: str) -> str:
    if not API_FOOT_KEY:
        return "La clé API foot est manquante côté serveur."
    team_id = _resolve_team_id(team_name)
    if not team_id:
        return f"Désolé, je ne trouve pas l'équipe « {team_name} ». Essaie : PSG, OM, Lyon, RC Lens, Monaco."
    url = f"{BASE_URL}/fixtures?team={team_id}&next=1"
    headers = {"x-apisports-key": API_FOOT_KEY}
    r = requests.get(url, headers=headers, timeout=12)
    if r.status_code != 200:
        return "Impossible de récupérer le prochain match pour cette équipe."
    data = r.json()
    if not data.get("response"):
        return "Pas de prochain match trouvé."
    match = data["response"][0]
    date = match["fixture"]["date"][:10]
    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]
    return f"Prochain match du {team_name} : {home} vs {away}, le {date}."

def generate_gpt_response(user_msg: str, data_json: dict) -> str:
    prompt = (
        "Tu es Lanai, un compagnon bienveillant pour Mohamed Djeziri. "
        "Tu parles simplement, en phrases courtes, sans jargon. "
        "Sa femme s'appelle Milouda, son chat Lana. "
        "Pour la santé: conseils généraux uniquement, jamais de diagnostic. "
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
    # FOOT (via intent + petite heuristique)
    if intent.get("intent") == "football":
        action = (intent.get("action") or "").lower()
        team = intent.get("team")

        # Si l'utilisateur parle de "match" sans action explicite -> on force "next_match"
        if not action and team and any(k in user_msg.lower() for k in ["match", "prochain", "joue quand", "calendrier"]):
            action = "next_match"

        if action == "next_match" and team:
            return get_next_match(team)

        # TODO : ajouter d'autres actions (score, calendar, injuries...) si tu veux
        return "Tu veux parler de foot ? Dis-moi l’équipe (ex : RC Lens, PSG, OM) et ce que tu veux (prochain match, score, calendrier)."

    # BASKET (à implémenter quand tu ajoutes une API basket)
    if intent.get("intent") == "basketball":
        return "Pour le basket, dis-moi l’équipe (ex : Lakers, Celtics) et ce que tu veux (prochain match, score)."

    # MÉTÉO (à implémenter quand tu ajoutes l’API météo)
    if intent.get("intent") == "weather":
        return "Pour la météo, donne-moi la ville et le jour (ex : Paris demain)."

    # Fallback → GPT compagnon
    return generate_gpt_response(user_msg, data_json)
