import re
from unidecode import unidecode

def _norm(s: str) -> str:
    return unidecode((s or "").lower().strip())

# Triggers
TR_NEXT   = ["prochain match", "prochain", "next"]
TR_LAST   = ["dernier match", "dernier", "last"]
TR_RES    = ["resultats", "résultats", "score", "scores", "resultat", "résultat"]
TR_CAL    = ["calendrier", "programme", "fixtures", "matches"]
TR_TAB    = ["classement", "ranking", "tableau"]
TR_NBA    = ["nba", "basket", "basketball"]
TR_FOOT   = ["foot", "football", "ligue 1", "premier league", "serie a", "bundesliga", "liga", "champions"]

MONTHS = ["janvier","fevrier","février","mars","avril","mai","juin","juillet","aout","août","septembre","octobre","novembre","decembre","décembre"]

def detect_sport(text: str) -> str | None:
    t = _norm(text)
    if any(k in t for k in TR_NBA):  return "basket"
    if any(k in t for k in TR_FOOT): return "foot"
    # si non précisé, on laisse None → on décidera par équipe/ligue
    return None

def extract_team(text: str) -> str | None:
    """
    Renvoie le nom d’équipe probable après avoir retiré les triggers.
    Ex: "prochain match psg", "résultat real madrid hier"
    """
    t = _norm(text)
    # enlève quelques mots fréquents
    for token in TR_NEXT + TR_LAST + TR_RES + TR_CAL + ["hier","aujourd","aujourd'hui","demain","le","la","les","du","de","des","match","matchs"]:
        t = t.replace(token, " ")
    t = re.sub(r"\s+", " ", t).strip()
    if not t: 
        return None
    # garde 2-4 mots max pour l’équipe
    words = t.split(" ")
    return " ".join(words[:4]).strip()

def extract_date_hint(text: str) -> str | None:
    t = _norm(text)
    if "hier" in t: return "yesterday"
    if "demain" in t: return "tomorrow"
    if any(m in t for m in MONTHS) or re.search(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", t):
        return t  # on renverra tel quel, le service tentera de parser
    return None

def detect_sport_intent(message: str) -> dict | None:
    t = _norm(message)
    if any(k in t for k in TR_NEXT + TR_LAST + TR_RES + TR_CAL + TR_TAB) or "match" in t:
        intent = None
        if any(k in t for k in TR_NEXT): intent = "SPORT_NEXT"
        elif any(k in t for k in TR_LAST): intent = "SPORT_LAST"
        elif any(k in t for k in TR_CAL): intent = "SPORT_CAL"
        elif any(k in t for k in TR_TAB): intent = "SPORT_TABLE"
        else: intent = "SPORT_RESULTS"

        return {
            "intent": intent,
            "sport": detect_sport(t),
            "team": extract_team(message),
            "date_hint": extract_date_hint(message)
        }
    return None
