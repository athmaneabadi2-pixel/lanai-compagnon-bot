import os
from datetime import datetime, timedelta, date
import pytz
import requests
from config import APISPORTS_KEY, FOOT_BASE, APP_TIMEZONE

H_FOOT = {"x-apisports-key": APISPORTS_KEY}

def _fmt_dt_iso_to_local(iso_str: str) -> str:
    # "2025-08-15T19:00:00+00:00" -> "15/08/2025 à 21:00" (selon Europe/Paris)
    tz = pytz.timezone(APP_TIMEZONE)
    dt_utc = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    dt_local = dt_utc.astimezone(tz)
    return dt_local.strftime("%d/%m/%Y à %H:%M")

def foot_search_team_id(name: str) -> int | None:
    if not name:
        return None
    r = requests.get(f"{FOOT_BASE}/teams", headers=H_FOOT, params={"search": name}, timeout=12)
    r.raise_for_status()
    resp = r.json().get("response", [])
    if not resp:
        return None
    return resp[0]["team"]["id"]

def foot_next_match(team_id: int) -> dict | None:
    r = requests.get(f"{FOOT_BASE}/fixtures", headers=H_FOOT, params={"team": team_id, "next": 1}, timeout=12)
    r.raise_for_status()
    arr = r.json().get("response", [])
    return arr[0] if arr else None

def foot_last_match(team_id: int) -> dict | None:
    r = requests.get(f"{FOOT_BASE}/fixtures", headers=H_FOOT, params={"team": team_id, "last": 1}, timeout=12)
    r.raise_for_status()
    arr = r.json().get("response", [])
    return arr[0] if arr else None

def _fixtures_by_date(team_id: int, d: date) -> list:
    # API-Sports permet "date=YYYY-MM-DD"
    r = requests.get(
        f"{FOOT_BASE}/fixtures",
        headers=H_FOOT,
        params={"team": team_id, "date": d.strftime("%Y-%m-%d")},
        timeout=12,
    )
    r.raise_for_status()
    return r.json().get("response", [])

def _render_fixture(fx: dict) -> str:
    league = fx["league"]["name"]
    when = _fmt_dt_iso_to_local(fx["fixture"]["date"])
    home = fx["teams"]["home"]["name"]
    away = fx["teams"]["away"]["name"]
    status = fx["fixture"]["status"]["short"]  # "NS", "FT", ...
    score = fx.get("goals", {})
    hs, as_ = score.get("home"), score.get("away")
    if status in ("FT", "AET", "PEN"):  # terminé
        return f"{league} – {home} {hs}-{as_} {away} (terminé le {when})."
    return f"{league} – {home} vs {away} (le {when})."

def sports_text_next(team_name: str) -> str:
    tid = foot_search_team_id(team_name)
    if not tid:
        return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    fx = foot_next_match(tid)
    if not fx:
        return f"Aucun prochain match trouvé pour « {team_name} »."
    return "Prochain match : " + _render_fixture(fx)

def sports_text_result_today(team_name: str) -> str:
    tid = foot_search_team_id(team_name)
    if not tid:
        return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    tz = pytz.timezone(APP_TIMEZONE)
    today = datetime.now(tz).date()
    fxs = _fixtures_by_date(tid, today)
    if fxs:
        # s'il y a plusieurs matchs (rare), on renvoie le premier
        return "Match du jour : " + _render_fixture(fxs[0])
    # sinon, renvoie le dernier match joué (utile si la demande tombe après minuit)
    last = foot_last_match(tid)
    if last:
        return "Dernier match : " + _render_fixture(last)
    return f"Aucun match aujourd’hui pour « {team_name} »."

def sports_text_result_yesterday(team_name: str) -> str:
    tid = foot_search_team_id(team_name)
    if not tid:
        return f"Je n’ai pas trouvé l’équipe « {team_name} »."
    tz = pytz.timezone(APP_TIMEZONE)
    yday = (datetime.now(tz) - timedelta(days=1)).date()
    fxs = _fixtures_by_date(tid, yday)
    if fxs:
        return "Match d’hier : " + _render_fixture(fxs[0])
    # fallback: dernier match
    last = foot_last_match(tid)
    if last:
        return "Dernier match : " + _render_fixture(last)
    return f"Aucun match trouvé hier pour « {team_name} »."

def sports_dispatch(intent: str, team: str | None) -> str:
    if not team:
        return "Dis-moi l’équipe exacte (ex: PSG) et je te réponds."
    if intent == "SPORT_NEXT":
        return sports_text_next(team)
    if intent == "SPORT_RESULT_TODAY":
        return sports_text_result_today(team)
    if intent == "SPORT_RESULT_YESTERDAY":
        return sports_text_result_yesterday(team)
    # fallback
    return sports_text_next(team)
