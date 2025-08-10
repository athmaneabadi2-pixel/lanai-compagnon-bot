import re
from unidecode import unidecode

def _norm(s: str) -> str:
    return unidecode((s or "").lower().strip())

# ex: "Météo de demain à Loffre" → Loffre
_CITY_RE = re.compile(r"(?:\b(a|à|sur|pour)\s+)([a-zA-ZÀ-ÖØ-öø-ÿ\-\s']+)$", re.IGNORECASE)

def _extract_city(text: str) -> str | None:
    m = _CITY_RE.search(text.strip())
    return m.group(2).strip().title() if m else None

def _extract_team(text: str) -> str | None:
    t = _norm(text)
    if "psg" in t or "paris saint" in t:
        return "PSG"
    return None

def route(message: str) -> dict:
    t = _norm(message)

    # 1) Prochain match (ordre d'abord car très spécifique)
    if ("prochain" in t and "match" in t) or "prochain match" in t:
        return {"intent": "NEXT_MATCH", "team": _extract_team(message) or "PSG"}

    # 2) Météo (aujourd'hui / demain / ville)
    if "meteo" in t or "météo" in message.lower():
        when = "demain" if "demain" in t else "aujourdhui"
        city = _extract_city(message)
        return {"intent": "WEATHER", "when": when, "city": city}

    # 3) Date / heure
    if "date" in t or "aujourdhui" in t or "aujourd" in t or "heure" in t:
        return {"intent": "DATE"}

    # 4) Souvenirs / mémoire
    if any(w in t for w in ["souvenir", "souvenirs", "memoire", "mémoire", "enfants", "enfant", "femme", "épouse"]):
        return {"intent": "MEMORY"}

    # 5) Small talk
    if any(w in t for w in ["bonjour", "salut", "ca va", "ça va"]):
        return {"intent": "SMALLTALK"}

    # 6) Fallback GPT
    return {"intent": "GPT"}
