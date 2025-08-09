# response_generator.py
import os
import requests
from openai import OpenAI

client_ai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

API_FOOT_KEY = os.environ.get("API_FOOT_KEY")
BASE_URL = "https://v3.football.api-sports.io"

# Petite base d'ID équipe (à compléter)
TEAM_IDS = {
    "PSG": 85, "Paris SG": 85, "Paris": 85,
    "OM": 81, "Marseille": 81,
    "Lyon": 80,
    "RC Lens": 116, "Lens": 116,
    "Monaco": 91,
}

def get_next_match(team_name: str) -> str:
    team_id = TEAM_IDS.get(team_name)
    if not team_id:
        return f"Désolé, je ne trouve pas l'équipe « {team_name} »."
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
    return f"Le prochain match du {team_name} : {home} vs {away}, le {date}."

def generate_gpt_response(user_msg: str, data_json: dict) -> str:
    prompt = (
        "Tu es Lanai, un compagnon bienveillant pour Mohamed Djeziri. "
        "Tu parles simplement, en phrases courtes, sans jargon. "
        "Sa femme s'appelle Milouda, son chat Lana. "
        "Si c'est de la santé, reste général (pas de diagnostic). "
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
    # FOOT
    if intent.get("intent") == "football":
        action = intent.get("action")
        team = intent.get("team")
        if action == "next_match" and team:
            return get_next_match(team)
        # TODO: autres actions (score, calendar, injury_status...)
        return "Tu veux parler de foot ? Précise l’équipe, la date ou le joueur 🙂"

    # BASKET (ex: à implémenter avec ton API basket)
    if intent.get("intent") == "basketball":
        return "Fonction basket à ajouter (calendrier, score, joueurs)."

    # MÉTÉO (ex: à implémenter avec ton API météo)
    if intent.get("intent") == "weather":
        return "Je peux te dire la météo si tu me donnes la ville et le jour 🙂"

    # PAR DÉFAUT → GPT compagnon
    return generate_gpt_response(user_msg, data_json)
