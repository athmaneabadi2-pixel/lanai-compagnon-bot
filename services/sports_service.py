import requests, pytz, re
from datetime import datetime, timedelta
from config import API_FOOT_KEY, API_BASKET_KEY, APP_TIMEZONE

TZ = pytz.timezone(APP_TIMEZONE)

FOOT_BASE = "https://v3.football.api-sports.io"
NBA_BASE  = "https://v1.basketball.api-sports.io"

H_FOOT = {"x-apisports-key": API_FOOT_KEY}
H_BASK = {"x-apisports-key": API_BASKET_KEY}

# ---------- Utils ----------
def _parse_date_hint(date_hint: str | None) -> str | None:
    if not date_hint: return None
    t = date_hint.lower()
    if "yesterday" in t or "hier" in t:
        return (datetime.now(TZ) - timedelta(days=1)).strftime("%Y-%m-%d")
    if "tomorrow" in t or "demain" in t:
        return (datetime.now(TZ) + timedelta(days=1)).strftime("%Y-%m-%d")
    m = re.search(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", t)
    if m:
        d, M, y = int(m.group(1)), int(m.group(2)), m.group(3)
        y = int(y) + 2000 if y and len(y)==2 else int(y) if y else datetime.now(TZ).year
        try:
            return datetime(y,M,d).strftime("%Y-%m-%d")
        except Exception:
            return None
    return None

# ---------- FOOT ----------
def foot_search_team(name: str) -> int | None:
    if not name: return None
    # recherche large
    url = f"{FOOT_BASE}/teams"
    r = requests.get(url, headers=H_FOOT, params={"search": name}, timeout=10)
    r.raise_for_status()
    resp = r.json().get("response", [])
    return resp[0]["team"]["id"] if resp else None

def foot_next(team_name: str) -> str:
    tid = foot_search_team(team_name)
    if not tid: return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    r = requests.get(f"{FOOT_BASE}/fixtures", headers=H_FOOT, params={"team": tid, "next": 1}, timeout=10)
    r.raise_for_status()
    js = r.json().get("response", [])
    if not js: return f"Aucun match à venir trouvé pour {team_name}."
    fx = js[0]
    dt = datetime.fromisoformat(fx["fixture"]["date"].replace("Z","+00:00")).astimezone(TZ)
    home, away = fx["teams"]["home"]["name"], fx["teams"]["away"]["name"]
    adv = away if fx["teams"]["home"]["id"]==tid else home
    comp = f'{fx["league"]["name"]} {fx["league"]["season"]}'
    return f"Prochain match {team_name.title()} : {adv} – {comp}, le {dt.strftime('%d/%m à %H:%M')}."

def foot_last(team_name: str) -> str:
    tid = foot_search_team(team_name)
    if not tid: return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    r = requests.get(f"{FOOT_BASE}/fixtures", headers=H_FOOT, params={"team": tid, "last": 1}, timeout=10)
    r.raise_for_status()
    js = r.json().get("response", [])
    if not js: return f"Aucun match récent trouvé pour {team_name}."
    fx = js[0]
    h, a = fx["teams"]["home"]["name"], fx["teams"]["away"]["name"]
    hs, as_ = fx["goals"]["home"], fx["goals"]["away"]
    return f"Dernier match {team_name.title()} : {h} {hs} – {a} {as_}."

def foot_results_by_date(date_str: str) -> str:
    r = requests.get(f"{FOOT_BASE}/fixtures", headers=H_FOOT, params={"date": date_str}, timeout=10)
    r.raise_for_status()
    resp = r.json().get("response", [])
    if not resp: return f"Aucun match trouvé le {datetime.fromisoformat(date_str).strftime('%d/%m')}."
    sample = resp[0]
    h, a = sample["teams"]["home"]["name"], sample["teams"]["away"]["name"]
    hs, as_ = sample["goals"]["home"], sample["goals"]["away"]
    return f"Le {datetime.fromisoformat(date_str).strftime('%d/%m')}: ex. {h} {hs} – {a} {as_} ({len(resp)} matchs)."

def foot_calendar(team_name: str, n=3) -> str:
    tid = foot_search_team(team_name)
    if not tid: return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    r = requests.get(f"{FOOT_BASE}/fixtures", headers=H_FOOT, params={"team": tid, "next": n}, timeout=10)
    r.raise_for_status()
    resp = r.json().get("response", [])
    if not resp: return f"Aucun match à venir pour {team_name}."
    lines = []
    for fx in resp:
        dt = datetime.fromisoformat(fx["fixture"]["date"].replace("Z","+00:00")).astimezone(TZ)
        home, away = fx["teams"]["home"]["name"], fx["teams"]["away"]["name"]
        lines.append(f"{dt.strftime('%d/%m %H:%M')} – {home} vs {away} ({fx['league']['name']})")
    return f"Calendrier {team_name.title()}:\n" + "\n".join(lines)

def foot_table(league: str | None) -> str:
    # essaie Ligue 1 par défaut si league None
    lg = league or "Ligue 1"
    r = requests.get(f"{FOOT_BASE}/standings", headers=H_FOOT, params={"season": datetime.now(TZ).year, "league": 61}, timeout=10) if lg.lower().startswith("ligue 1") else None
    if not r:
        return "Classement: pour l’instant je gère surtout la Ligue 1."
    r.raise_for_status()
    table = r.json()["response"][0]["league"]["standings"][0][:5]
    top = ", ".join([f"{row['rank']}. {row['team']['name']}" for row in table])
    return f"Top Ligue 1: {top}."

# ---------- BASKET ----------
def bask_search_team(name: str) -> int | None:
    if not name: return None
    r = requests.get(f"{NBA_BASE}/teams", headers=H_BASK, params={"search": name}, timeout=10)
    r.raise_for_status()
    resp = r.json().get("response", [])
    return resp[0]["id"] if resp else None

def bask_next(team_name: str) -> str:
    tid = bask_search_team(team_name)
    if not tid: return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    r = requests.get(f"{NBA_BASE}/games", headers=H_BASK, params={"team": tid, "next": 1}, timeout=10)
    r.raise_for_status()
    js = r.json().get("response", [])
    if not js: return f"Aucun match à venir trouvé pour {team_name}."
    g = js[0]
    dt = datetime.fromisoformat(g["date"]["start"].replace("Z","+00:00")).astimezone(TZ)
    h, a = g["teams"]["home"]["name"], g["teams"]["visitors"]["name"]
    return f"Prochain match {team_name.title()} : {h} vs {a}, le {dt.strftime('%d/%m à %H:%M')}."

def bask_last(team_name: str) -> str:
    tid = bask_search_team(team_name)
    if not tid: return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    r = requests.get(f"{NBA_BASE}/games", headers=H_BASK, params={"team": tid, "last": 1}, timeout=10)
    r.raise_for_status()
    js = r.json().get("response", [])
    if not js: return f"Aucun match récent pour {team_name}."
    g = js[0]
    h, a = g["teams"]["home"]["name"], g["teams"]["visitors"]["name"]
    hs, as_ = g["scores"]["home"]["points"], g["scores"]["visitors"]["points"]
    return f"Dernier match {team_name.title()} : {h} {hs} – {a} {as_}."

def bask_results_by_date(date_str: str) -> str:
    r = requests.get(f"{NBA_BASE}/games", headers=H_BASK, params={"date": date_str}, timeout=10)
    r.raise_for_status()
    resp = r.json().get("response", [])
    if not resp: return f"Aucun match le {datetime.fromisoformat(date_str).strftime('%d/%m')}."
    g = resp[0]
    h, a = g["teams"]["home"]["name"], g["teams"]["visitors"]["name"]
    hs, as_ = g["scores"]["home"]["points"], g["scores"]["visitors"]["points"]
    return f"Le {datetime.fromisoformat(date_str).strftime('%d/%m')}: ex. {h} {hs} – {a} {as_} ({len(resp)} matchs)."

def bask_calendar(team_name: str, n=3) -> str:
    tid = bask_search_team(team_name)
    if not tid: return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    r = requests.get(f"{NBA_BASE}/games", headers=H_BASK, params={"team": tid, "next": n}, timeout=10)
    r.raise_for_status()
    resp = r.json().get("response", [])
    if not resp: return f"Aucun match à venir pour {team_name}."
    lines = []
    for g in resp:
        dt = datetime.fromisoformat(g["date"]["start"].replace("Z","+00:00")).astimezone(TZ)
        h, a = g["teams"]["home"]["name"], g["teams"]["visitors"]["name"]
        lines.append(f"{dt.strftime('%d/%m %H:%M')} – {h} vs {a}")
    return f"Calendrier {team_name.title()}:\n" + "\n".join(lines)

# ---------- Routeur générique ----------
def sports_dispatch(intent: str, sport: str | None, team: str | None, date_hint: str | None) -> str:
    date_str = _parse_date_hint(date_hint)

    # heuristique : si team contient des mots très foot (psg, real, om…) → foot
    if not sport and team:
        if any(k in team.lower() for k in ["psg","paris","om","marseille","real","barca","arsenal","liverpool","bayern","juventus"]):
            sport = "foot"
        elif any(k in team.lower() for k in ["lakers","celtics","warriors","bulls","knicks","heat","spurs"]):
            sport = "basket"

    if intent == "SPORT_TABLE":
        return foot_table(None)

    if sport == "basket":
        if intent == "SPORT_NEXT":     return bask_next(team)
        if intent == "SPORT_LAST":     return bask_last(team)
        if intent == "SPORT_CAL":      return bask_calendar(team, n=3)
        return bask_results_by_date(date_str or datetime.now(TZ).strftime("%Y-%m-%d"))

    # défaut = foot
    if intent == "SPORT_NEXT":     return foot_next(team)
    if intent == "SPORT_LAST":     return foot_last(team)
    if intent == "SPORT_CAL":      return foot_calendar(team, n=3)
    return foot_results_by_date(date_str or datetime.now(TZ).strftime("%Y-%m-%d"))
