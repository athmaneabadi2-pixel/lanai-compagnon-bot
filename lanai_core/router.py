from unidecode import unidecode
from .sports_nlp import detect_sport_intent

def _norm(s: str) -> str:
    return unidecode((s or "").lower().strip())

def route(message: str) -> dict:
    t = _norm(message)

    # 0) SPORT (spécifique, en premier)
    sport = detect_sport_intent(message)
    if sport:
        return sport

    # 1) Météo
    if "meteo" in t or "météo" in message.lower():
        when = "demain" if "demain" in t else "aujourdhui"
        # ville si présente après "à"
        city = None
        if " a " in f" {t} " or " à " in message.lower():
            part = message.split("à")[-1].strip()
            if part:
                city = part.title()
        return {"intent": "METEO", "when": when, "city": city}

    # 2) Date/heure
    if "date" in t or "aujourdhui" in t or "aujourd" in t or "heure" in t:
        return {"intent": "DATE"}

    # 3) Mémoire
    if any(w in t for w in ["souvenir", "souvenirs", "memoire", "enfants", "enfant", "femme", "epouse", "chat", "animal", "nom"]):
        return {"intent": "MEMORY", "query": message}

    # 4) Small talk
    if any(w in t for w in ["bonjour", "salut", "ca va", "ça va"]):
        return {"intent": "SMALLTALK"}

    return {"intent": "FALLBACK"}
