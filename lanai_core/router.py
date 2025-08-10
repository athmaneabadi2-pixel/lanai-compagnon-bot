from lanai_core.memory import load_profile
from services.weather_service import weather_tomorrow_short
from services.sports_service import (
    nba_yesterday_summary, basket_europe_yesterday_summary,
    football_yesterday_summary, matches_yesterday_combo,
)
from services.openai_service import polish_for_mohamed, smalltalk

def handle_message(text: str) -> str:
    t = (text or "").lower()
    p = load_profile()

    # Saluts / chit-chat simple → GPT
    if any(k in t for k in ["ça va", "ca va", "merci", "bonjour", "salut", "hello", "hi"]):
        return smalltalk(p, text)

    # Météo (factuel → polish GPT)
    if "météo" in t or "meteo" in t:
        raw = weather_tomorrow_short(p.get("Identité", {}).get("Ville", "Paris"))
        return polish_for_mohamed(p, raw)

    # Basket / Foot (factuel → polish GPT)
    if "nba" in t:
        return polish_for_mohamed(p, nba_yesterday_summary())
    if any(k in t for k in ["basket france","basket fr","pro a","lnb","euroleague","eurocup","bcl"]):
        return polish_for_mohamed(p, basket_europe_yesterday_summary())

    if any(k in t for k in [
        "foot","football","ligue 1","premier league","la liga","liga","serie a","bundesliga",
        "champions league","ldc","europa","conference","france","algérie","algerie","maroc","morocco"
    ]):
        return polish_for_mohamed(p, football_yesterday_summary())

    if "match" in t:
        return polish_for_mohamed(p, matches_yesterday_combo())

    # Souvenir simple depuis la mémoire → polish optionnel
    if "souvenir" in t:
        sv = p.get("Souvenirs", {}).get("Fierté ou accomplissement") or "Un bon moment en famille."
        return polish_for_mohamed(p, f"Souvenir: {sv}")

    if "lana" in t:
        return smalltalk(p, "Parle de Lana avec douceur")

    # Par défaut → GPT (petite réponse douce)
    return smalltalk(p, text)
