from lanai_core.memory import load_profile
from services.weather_service import weather_tomorrow_short
from services.sports_service import (
    nba_yesterday_summary,
    basket_europe_yesterday_summary,
    football_yesterday_summary,
    matches_yesterday_combo,
)

def _prenom(p):
    return p.get("Identité", {}).get("Prénom", "Mohamed")

def handle_message(text: str) -> str:
    t = (text or "").lower()
    p = load_profile()
    name = _prenom(p)

    # Saluts
    if any(k in t for k in ["bonjour","salut","hello","hi"]):
        return f"Salut {name} 😊 Ça va aujourd’hui ?"

    # Météo
    if "météo" in t or "meteo" in t:
        ville = p.get("Identité", {}).get("Ville", "Paris")
        return weather_tomorrow_short(ville)

    # Basket
    if any(k in t for k in ["nba"]):
        return nba_yesterday_summary()
    if any(k in t for k in ["basket france", "basket fr", "pro a", "lnb", "euroleague", "eurocup", "bcl"]):
        return basket_europe_yesterday_summary()

    # Foot : ligues, coupes, nations
    if any(k in t for k in [
        "foot","football","ligue 1","premier league","la liga","liga","serie a","bundesliga",
        "champions league","ldc","europa","conference","france","algérie","algerie","maroc","morocco"
    ]):
        return football_yesterday_summary()

    # Mot "match" générique → combiné
    if "match" in t:
        return matches_yesterday_combo()

    # Souvenir / Lana
    if "souvenir" in t:
        sv = p.get("Souvenirs", {}).get("Fierté ou accomplissement") or "Un bon moment en famille."
        return f"Souvenir: {sv}"
    if "lana" in t:
        return "Une caresse pour Lana 🐱"

    return "Bien reçu. Je suis là si tu veux parler."
