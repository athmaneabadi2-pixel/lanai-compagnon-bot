# response_generator.py
import os, re, unicodedata, json, requests
from datetime import datetime
from zoneinfo import ZoneInfo
from babel.dates import format_datetime
from openai import OpenAI

# ====== ENV & Clients ======
client_ai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Accepte tes noms d'ENV actuels ou RAPIDAPI_KEY
RAPIDAPI_KEY = (
    os.environ.get("API_FOOT_KEY")
    or os.environ.get("API_BASKET_KEY")
    or os.environ.get("RAPIDAPI_KEY")
)

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
TZ = ZoneInfo("Europe/Paris")

# ====== Helpers ======
def _slug(txt: str) -> str:
    if not txt:
        return ""
    txt = unicodedata.normalize("NFKD", txt.lower().strip())
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", txt)

def today_fr() -> str:
    now = datetime.now(TZ)
    # Format FR fiable (pas besoin de locale système)
    return format_datetime(now, "EEEE d MMMM y", locale="fr")

def warm_prefix(profile: dict) -> str:
    name = (profile.get("Identité", {}) or {}).get("Prénom", "Mohamed")
    return f"Salut {name} ! "

# ====== METEO (OpenWeather One Call 3.0) ======
def weather_tomorrow(lat: float, lon: float) -> str:
    if not OPENWEATHER_API_KEY:
        return "Clé météo manquante (OPENWEATHER_API_KEY)."
    url = (
        "https://api.openweathermap.org/data/3.0/onecall"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr"
    )
    try:
        r = requests.get(url, timeout=12)
    except Exception:
        return "Le service météo ne répond pas."
    if r.status_code != 200:
        return f"Erreur météo ({r.status_code})."
    js = r.json()
    if "daily" not in js or not js["daily"]:
        return "Données météo indisponibles."
    d = js["daily"][1] if len(js["daily"]) > 1 else js["daily"][0]
    desc = d["weather"][0]["description"]
    tmin, tmax = round(d["temp"]["min"]), round(d["temp"]["max"])
    return f"Demain : {desc}, {tmin}–{tmax}°C."

# ====== FOOT (RapidAPI / API-FOOTBALL) ======
FOOT_HOST = "api-football-v1.p.rapidapi.com"
FOOT_BASE = f"https://{FOOT_HOST}/v3"

def foot_headers():
    return {"x-rapidapi-key": RAPIDAPI_KEY or "", "x-rapidapi-host": FOOT_HOST}

def foot_search_team(team_query: str):
    if not RAPIDAPI_KEY:
        return (None, None)
    try:
        r = requests.get(f"{FOOT_BASE}/teams", headers=foot_headers(),
                         params={"search": team_query}, timeout=12)
        if r.status_code != 200:
            return (None, None)
        resp = r.json().get("response", [])
        if not resp:
            return (None, None)
        team = resp[0]["team"]
        return team["id"], team["name"]
    except Exception:
        return (None, None)

def foot_next_match(team_name: str, season: int = 2025) -> str:
    if not RAPIDAPI_KEY:
        return "Clé sport manquante (API_FOOT_KEY / API_BASKET_KEY / RAPIDAPI_KEY)."
    team_id, canon = foot_search_team(team_name)
    if not team_id:
        return f"Désolé, je ne trouve pas l'équipe « {team_name} »."
    try:
        r = requests.get(f"{FOOT_BASE}/fixtures", headers=foot_headers(),
                         params={"team": team_id, "season": season, "next": 1, "timezone": "Europe/Paris"},
                         timeout=12)
    except Exception:
        return "Le service foot ne répond pas."
    if r.status_code != 200:
        return "Impossible de récupérer le prochain match."
    resp = r.json().get("response", [])
    if not resp:
        return f"Pas de prochain match trouvé pour {canon}."
    m = resp[0]
    date_iso = m["fixture"]["date"]
    try:
        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00")).astimezone(TZ)
        date_str = dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        date_str = date_iso[:10]
    home = m["teams"]["home"]["name"]
    away = m["teams"]["away"]["name"]
    return f"Prochain match de {canon} : {home} vs {away}, le {date_str}."

# ====== NBA (RapidAPI / API-NBA) ======
NBA_HOST = "api-nba-v1.p.rapidapi.com"
NBA_BASE = f"https://{NBA_HOST}"

def nba_headers():
    return {"x-rapidapi-key": RAPIDAPI_KEY or "", "x-rapidapi-host": NBA_HOST}

def nba_search_team(team_query: str):
    if not RAPIDAPI_KEY:
        return (None, None)
    try:
        r = requests.get(f"{NBA_BASE}/teams", headers=nba_headers(),
                         params={"search": team_query}, timeout=12)
        if r.status_code != 200:
            return (None, None)
        resp = r.json().get("response", [])
        if not resp:
            return (None, None)
        team = resp[0]
        return team["id"], team["name"]
    except Exception:
        return (None, None)

def nba_next_game(team_name: str, season: int = 2024) -> str:
    if not RAPIDAPI_KEY:
        return "Clé sport manquante (API_FOOT_KEY / API_BASKET_KEY / RAPIDAPI_KEY)."
    team_id, canon = nba_search_team(team_name)
    if not team_id:
        return f"Désolé, je ne trouve pas l’équipe NBA « {team_name} »."
    try:
        r = requests.get(f"{NBA_BASE}/games", headers=nba_headers(),
                         params={"season": season, "team": team_id, "next": 1, "timezone": "Europe/Paris"},
                         timeout=12)
    except Exception:
        return "Le service NBA ne répond pas."
    if r.status_code != 200:
        return "Impossible de récupérer le prochain match NBA."
    resp = r.json().get("response", [])
    if not resp:
        return f"Pas de prochain match trouvé pour {canon}."
    g = resp[0]
    date_iso = g["date"]["start"]
    try:
        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00")).astimezone(TZ)
        date_str = dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        date_str = date_iso[:10]
    home = g["teams"]["home"]["name"]
    away = g["teams"]["away"]["name"]
    return f"Prochain match des {canon} : {home} vs {away}, le {date_str}."

# ====== GPT compagnon ======
def generate_gpt_response(user_msg: str, profile: dict) -> str:
    prompt = (
        "Tu es Lanai, compagnon WhatsApp pour Mohamed Djeziri. "
        "Style simple, phrases courtes, chaleureux. "
        "Souviens‑toi: Milouda (épouse), Lana (chat). "
        "Pas de diagnostic médical.\n\n"
        f"Profil: {json.dumps(profile, ensure_ascii=False)}\n"
        f"Message: « {user_msg} »"
    )
    resp = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()

# ====== ROUTAGE ======
def generate_response(intent: dict, user_msg: str, profile: dict) -> str:
    text = (user_msg or "").lower().strip()

    # 0) Date du jour (FR garanti)
    if any(k in text for k in ["quelle date", "quel jour", "date d'aujourd"]):
        return warm_prefix(profile) + f"Aujourd’hui, nous sommes le {today_fr()}."

    sport = (intent.get("intent") or "").lower()
    action = (intent.get("action") or "").lower()
    team = intent.get("team")

    # Heuristique si action manquante mais on parle de match
    if not action and any(k in text for k in ["prochain", "match", "jouent", "calendrier"]):
        action = "next_match"

    # 1) METEO
    if sport == "weather" or "meteo" in text or "météo" in text:
        loc = (profile.get("location") or {})
        lat, lon = loc.get("lat", 50.433), loc.get("lon", 2.833)  # défaut: Lens
        return warm_prefix(profile) + weather_tomorrow(lat, lon)

    # 2) FOOT
    if sport == "football":
        if action == "next_match" and team:
            return warm_prefix(profile) + foot_next_match(team)
        return warm_prefix(profile) + "Dis-moi l’équipe (ex: PSG, RC Lens) et ce que tu veux (prochain match, score)."

    # 3) BASKET
    if sport == "basketball":
        if action == "next_match" and team:
            return warm_prefix(profile) + nba_next_game(team)
        return warm_prefix(profile) + "Pour le basket, donne-moi l’équipe (ex: Los Angeles Lakers)."

    # 4) Carte vitale / Voyage Algérie (lecture profil)
    if "carte vitale" in text:
        cv = (profile.get("carte_vitale") or {})
        if not cv:
            return warm_prefix(profile) + "Je n’ai pas trouvé l’info carte vitale."
        st, note = cv.get("statut", "inconnu"), cv.get("note", "")
        return warm_prefix(profile) + f"Carte vitale : {st}" + (f" – {note}" if note else "")

    if "algérie" in text or "algerie" in text or "voyage" in text:
        trip = (profile.get("voyage_algerie") or {})
        if not trip:
            return warm_prefix(profile) + "Je n’ai pas trouvé d’infos sur le voyage en Algérie."
        date = trip.get("date", "date à confirmer"); ville = trip.get("ville", "")
        return warm_prefix(profile) + f"Voyage en Algérie : {(ville + ' – ') if ville else ''}{date}"

    # 5) Fallback GPT
    return warm_prefix(profile) + generate_gpt_response(user_msg, profile)
