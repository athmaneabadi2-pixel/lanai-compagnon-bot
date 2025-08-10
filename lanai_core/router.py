from lanai_core.memory import load_profile
from services.weather_service import weather_tomorrow_short
from services.sports_service import nba_yesterday_summary

def _prenom(p):
    ident = p.get("Identité", {})
    return ident.get("Prénom", "Mohamed")

def handle_message(text: str) -> str:
    t = (text or "").lower()
    p = load_profile()
    name = _prenom(p)

    if any(k in t for k in ["bonjour","salut","hello","hi"]):
        return f"Salut {name} 😊 Ça va aujourd’hui ?"
    if "météo" in t or "meteo" in t:
        ville = p.get("Identité", {}).get("Ville", "Paris")
        return weather_tomorrow_short(ville)
    if "match" in t or "nba" in t:
        return nba_yesterday_summary()
    if "souvenir" in t:
        sv = p.get("Souvenirs", {}).get("Fierté ou accomplissement") or "Un bon moment en famille."
        return f"Souvenir: {sv}"
    if "lana" in t:
        return "Une caresse pour Lana 🐱"
    return "Bien reçu. Je suis là si tu veux parler."
