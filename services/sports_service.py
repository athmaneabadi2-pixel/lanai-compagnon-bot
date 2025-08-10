import os
import requests
from config import APISPORTS_KEY, FOOT_BASE
from lanai_core.sports_nlp import extract_team, extract_date_hint

H_FOOT = {"x-apisports-key": APISPORTS_KEY}

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
    # prochain match par équipe
    r = requests.get(f"{FOOT_BASE}/fixtures", headers=H_FOOT, params={"team": team_id, "next": 1}, timeout=12)
    r.raise_for_status()
    arr = r.json().get("response", [])
    return arr[0] if arr else None

def sports_dispatch(intent: str, sport: str | None, team: str | None, date_hint: str | None) -> str:
    # Pour l’instant : football uniquement (PSG, OM, etc.)
    team_name = team or ""
    if not team_name:
        # Essaie d’extraire de la phrase si le routeur n’a pas mis team
        team_name = sport or ""  # fallback ultra simple
    team_name = team_name or ""

    # essaye extraction NLP si vide
    if not team_name:
        return "Dis-moi l’équipe exacte (ex: PSG) et je te dis le prochain match."

    team_id = foot_search_team_id(team_name)
    if not team_id:
        return f"Je n’ai pas trouvé l’équipe « {team_name} »."

    fx = foot_next_match(team_id)
    if not fx:
        return f"Je n’ai pas de prochain match pour « {team_name} »."

    league = fx["league"]["name"]
    da = fx["fixture"]["date"]  # ISO
    home = fx["teams"]["home"]["name"]
    away = fx["teams"]["away"]["name"]

    vs = f"{home} vs {away}"
    return f"Prochain match ({league}) : {vs} – {da[:16].replace('T', ' à ')} (heure UTC)."
