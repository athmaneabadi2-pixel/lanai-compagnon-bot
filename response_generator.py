# response_generator.py
import os
import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from openai import OpenAI

client_ai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

# ---------- Helpers texte ----------
def _slug(txt: str) -> str:
    if not txt:
        return ""
    txt = txt.lower().strip()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = re.sub(r"\s+", " ", txt)
    return txt

def today_paris() -> str:
    try:
        return datetime.now(ZoneInfo("Europe/Paris")).strftime("%A %d %B %Y").capitalize()
    except Exception:
        return datetime.now().strftime("%A %d %B %Y").capitalize()

# ---------- FOOT (RapidAPI / API-FOOTBALL) ----------
FOOT_HOST = "api-football-v1.p.rapidapi.com"
FOOT_BASE = f"https://{FOOT_HOST}/v3"

def foot_headers():
    return {
        "x-rapidapi-key": RAPIDAPI_KEY or "",
        "x-rapidapi-host": FOOT_HOST
    }

def foot_search_team(team_query: str):
    """Recherche l'équipe et renvoie (team_id, canonical_name) ou (None, None)."""
    if not RAPIDAPI_KEY:
        return None, None
    url = f"{FOOT_BASE}/teams"
    params = {"search": team_query}
    try:
        r = requests.get(url, headers=foot_headers(), params=params, timeout=12)
        if r.status_code != 200:
            return None, None
        data = r.json()
        resp = data.get("response", [])
        if not resp:
            return None, None
        team = resp[0]["team"]
        return team["id"], team["name"]
    except Exception:
        return None, None

def foot_next_match(team_name: str, season: int = 2025) -> str:
    """Prochain match (saison courante forcée pour éviter les vieux résultats)."""
    team_id, canon = foot_search_team(team_name)
    if not team_id:
        return f"Désolé, je ne trouve pas l'équipe « {team_name} »."
    url = f"{FOOT_BASE}/fixtures"
    params = {"team": team_id, "season": season, "next": 1, "timezone": "Europe/Paris"}
    try:
        r = requests.get(url, headers=foot_headers(), params=params, timeout=12)
    except Exception:
        return "Le service des matchs de foot ne répond pas pour le moment."
    if r.status_code != 200:
        return "Impossible de récupérer le prochain match pour cette équipe."
    data = r.json()
    resp = data.get("response", [])
    if not resp:
        return f"Pas de prochain match trouvé pour {canon}."
    match = resp[0]
    date_iso = match["fixture"]["date"]
    try:
        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Paris"))
        date_str = dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        date_str = date_iso[:10]
    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]
    return f"Prochain match de {canon} : {home} vs {away}, le {date_str}."

# ---------- NBA (RapidAPI / API-NBA) ----------
NBA_HOST = "api-nba-v1.p.rapidapi.com"
NBA_BASE = f"https://{NBA_HOST}"

def nba_headers():
    return {
        "x-rapidapi-key": RAPIDAPI_KEY or "",
        "x-rapidapi-host": NBA_HOST
    }

def nba_search_team(team_query: str):
    """Renvoie (team_id, canonical_name) via /teams?search="""
    if not RAPIDAPI_KEY:
        return None, None
    url = f"{NBA_BASE}/teams"
    params = {"search": team_query}
    try:
        r = requests.get(url, headers=nba_headers(), params=params, timeout=12)
        if r.status_code != 200:
            return None, None
        data = r.json()
        resp = data.get("response", [])
        if not resp:
            return None, None
        team = resp[0]
        return team["id"], team["name"]
    except Exception:
        return None, None

def nba_next_game(team_name: str, season: int = 2024) -> str:
    """Prochain match NBA pour la saison donnée (à ajuster selon la saison courante)."""
    team_id, canon = nba_search_team(team_name)
    if not team_id:
        return f"Désolé, je ne trouve pas l’équipe NBA « {team_name} »."
    url = f"{NBA_BASE}/games"
    params = {"season": season, "team": team_id, "next": 1, "timezone": "Europe/Paris"}
    try:
        r = requests.get(url, headers=nba_headers(), params=params, timeout=12)
    except Exception:
        return "Le service des matchs NBA ne répond pas pour le moment."
    if r.status_code != 200:
        return "Impossible de récupérer le prochain match pour cette équipe NBA."
    data = r.json()
    resp = data.get("response", [])
    if not resp:
        return f"Pas de prochain match trouvé pour {canon}."
    game = resp[0]
    date_iso = game["date"]["start"]
    try:
        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Paris"))
        date_str = dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        date_str = date_iso[:10]
    home = game["teams"]["home"]["name"]
    away = game["teams"]["away"]["name"]
    return f"Prochain match des {canon} : {home} vs {away}, le {date_str}."

# ---------- GPT compagnon ----------
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

# --- ROUTING ---
def generate_response(intent: dict, user_msg: str, data_json: dict) -> str:
    text = user_msg.lower()

    # Date du jour
    if "quelle date" in text or "quel jour" in text or "date d'aujourd" in text:
        return f"Aujourd’hui, nous sommes le {today_paris()}."

    sport = (intent.get("intent") or "").lower()
    action = (intent.get("action") or "").lower()
    team = intent.get("team")

    # Heuristique : si pas d'action mais on parle de "match" => next_match
    if not action and any(k in text for k in ["prochain", "match", "jouent quand", "jouent?"]):
        action = "next_match"

    # FOOT
    if sport == "football":
        if action == "next_match" and team:
            return foot_next_match(team)
        return "Tu veux parler de foot ? Donne-moi l’équipe (ex : RC Lens, PSG, OM) et ce que tu veux (prochain match, score)."

    # BASKET
    if sport == "basketball":
        if action == "next_match" and team:
            return nba_next_game(team)
        return "Pour le basket, donne-moi l’équipe (ex : Los Angeles Lakers) et je te donne le prochain match."

    # MÉTÉO (placeholder)
    if sport == "weather":
        return "Pour la météo, donne-moi la ville et le jour (ex : Paris demain)."

    # Fallback → GPT compagnon
    return generate_gpt_response(user_msg, data_json)
