# services/sports_service.py
import requests, datetime
from config import APISPORTS_KEY_BASKET, APISPORTS_KEY_FOOT

def _yesterday_iso():
    return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

# ---------- BASKET : NBA ----------
def nba_yesterday_summary() -> str:
    if not APISPORTS_KEY_BASKET:
        return "Résultats NBA indisponibles (clé API manquante)."
    date = _yesterday_iso()
    url = "https://v1.basketball.api-sports.io/games"
    headers = {"x-apisports-key": APISPORTS_KEY_BASKET}
    try:
        r = requests.get(url, params={"date": date}, headers=headers, timeout=20)
    except Exception:
        return "Résultats NBA indisponibles (réseau)."
    if r.status_code != 200:
        return "Résultats NBA indisponibles."
    games = [g for g in (r.json().get("response") or [])
             if (g.get("league", {}).get("name", "").upper() == "NBA")]
    if not games:
        return "Pas de match NBA hier."
    out = []
    for g in games[:3]:
        h = g["teams"]["home"]["name"]; a = g["teams"]["away"]["name"]
        hs = g["scores"]["home"]["total"]; as_ = g["scores"]["away"]["total"]
        if hs is None or as_ is None:  # sécurité
            continue
        out.append(f"{a} {as_} – {h} {hs}")
    return "NBA (hier): " + " | ".join(out) if out else "Pas de scores NBA disponibles."

# ---------- BASKET : FR / EUROPE ----------
def basket_europe_yesterday_summary() -> str:
    """LNB Pro A, EuroLeague, EuroCup, BCL (filtre par nom de ligue)."""
    if not APISPORTS_KEY_BASKET:
        return "Basket Europe indisponible (clé API manquante)."
    date = _yesterday_iso()
    url = "https://v1.basketball.api-sports.io/games"
    headers = {"x-apisports-key": APISPORTS_KEY_BASKET}
    try:
        r = requests.get(url, params={"date": date}, headers=headers, timeout=20)
    except Exception:
        return "Basket Europe indisponible (réseau)."
    if r.status_code != 200:
        return "Basket Europe indisponible."
    wanted = ["pro a", "lnb", "euroleague", "eurocup", "basketball champions league"]
    games = []
    for g in (r.json().get("response") or []):
        lname = (g.get("league", {}).get("name") or "").lower()
        if any(w in lname for w in wanted):
            games.append(g)
    if not games:
        return "Pas de match majeur hier en basket européen."
    out = []
    for g in games[:3]:
        league = g["league"]["name"]
        h = g["teams"]["home"]["name"]; a = g["teams"]["away"]["name"]
        hs = g["scores"]["home"]["total"]; as_ = g["scores"]["away"]["total"]
        if hs is None or as_ is None:
            continue
        out.append(f"{league}: {a} {as_} – {h} {hs}")
    return "Basket 🇫🇷/🇪🇺 (hier): " + " | ".join(out) if out else "Pas de scores disponibles."

# ---------- FOOT : TOP LIGUES + COUPES + NATIONAUX (FR/ALG/MAR) ----------
def football_yesterday_summary() -> str:
    """Filtre sur top championnats, compétitions UEFA, et sélections FR/ALG/MAR."""
    if not APISPORTS_KEY_FOOT:
        return "Résultats foot indisponibles (clé API manquante)."
    date = _yesterday_iso()
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": APISPORTS_KEY_FOOT}
    try:
        r = requests.get(url, params={"date": date, "timezone": "Europe/Paris"}, headers=headers, timeout=25)
    except Exception:
        return "Résultats foot indisponibles (réseau)."
    if r.status_code != 200:
        return "Résultats foot indisponibles."

    leagues_whitelist = {
        "Ligue 1", "Premier League", "La Liga", "Serie A", "Bundesliga",
        "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League"
    }
    national_teams = {"France", "Algérie", "Algeria", "Maroc", "Morocco"}

    fixtures = r.json().get("response") or []
    selected = []
    for fx in fixtures:
        league = fx.get("league", {})
        league_name = league.get("name") or ""
        teams = fx.get("teams", {})
        home = teams.get("home", {}).get("name") or ""
        away = teams.get("away", {}).get("name") or ""
        goals = fx.get("goals", {})
        hs, as_ = goals.get("home"), goals.get("away")
        if hs is None or as_ is None:
            continue
        if (league_name in leagues_whitelist) or (home in national_teams) or (away in national_teams):
            selected.append((league_name, away, as_, home, hs))

    if not selected:
        return "Pas de match majeur hier en foot."
    lines = []
    for league, a, as_, h, hs in selected[:3]:
        lines.append(f"{league}: {a} {as_} – {h} {hs}")
    return "Foot (hier): " + " | ".join(lines)

# ---------- COMBINÉ ----------
def matches_yesterday_combo() -> str:
    """Petit résumé combiné quand l’utilisateur dit juste 'match'."""
    nba = nba_yesterday_summary()
    foot = football_yesterday_summary()
    return f"{nba}\n{foot}"
