import re
from datetime import datetime, timedelta
import unicodedata

# Normalise accents
def norm(s: str) -> str:
    s = (s or "").strip().lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

# dictionnaire d’alias d’équipes courantes FR
TEAM_ALIASES = {
    r"\bpsg\b|paris\s*sg|paris\s*saint[-\s]*germain": "psg",
    r"\bom\b|marseille": "marseille",
    r"\bol\b|lyon": "lyon",
    r"\blosc\b|lille": "lille",
    r"\blens\b|rclens|rc\s*lens": "lens",
    r"\bnantes\b": "nantes",
    r"\bnice\b": "nice",
    r"\bmonaco\b|asm": "monaco",
    r"\brennes\b": "rennes",
    r"\bmontpellier\b": "montpellier",
    r"\breims\b": "reims",
    r"\bbrest\b": "brest",
    r"\btoulouse\b": "toulouse",
    r"\bstrasbourg\b": "strasbourg",
}

PAT_NEXT = re.compile(r"\b(prochain|next)\b|\bcalendrier\b|\bprogramme\b", re.I)
PAT_TODAY = re.compile(r"\b(aujourd['’]?hui|today)\b", re.I)
PAT_YDAY = re.compile(r"\b(hier|yesterday)\b", re.I)
PAT_RESULT = re.compile(r"\b(resultat|score|a\s*fait\s*quoi|a\s*gagn[eé])\b", re.I)

def extract_team(user_text: str) -> str | None:
    t = norm(user_text)
    for pat, canonical in TEAM_ALIASES.items():
        if re.search(pat, t, re.I):
            return canonical
    # fallback naïf: prend le dernier mot >= 3 lettres
    words = [w for w in re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ\-]+", t) if len(w) >= 3]
    return words[-1] if words else None

def detect_sport_intent(user_text: str) -> dict:
    """
    Renvoie: {"intent": "SPORT_NEXT|SPORT_RESULT_TODAY|SPORT_RESULT_YESTERDAY", "team": "<str>"}
    ou {} si rien.
    """
    if not user_text:
        return {}
    team = extract_team(user_text)
    # on déclenche si on voit "match", "résultat", etc. ou si team explicite (psg, om...)
    t = user_text.lower()

    if PAT_NEXT.search(t) or "prochain match" in t or ("match" in t and "prochain" in t):
        return {"intent": "SPORT_NEXT", "team": team}

    if PAT_TODAY.search(t) and ("result" in t or "score" in t or "a fait quoi" in t or "match" in t):
        return {"intent": "SPORT_RESULT_TODAY", "team": team}

    if PAT_YDAY.search(t) or ("hier" in t and (PAT_RESULT.search(t) or "match" in t)):
        return {"intent": "SPORT_RESULT_YESTERDAY", "team": team}

    # si on demande "résultat psg" sans date, on regarde d’abord aujourd’hui, sinon dernier match
    if PAT_RESULT.search(t) or ("match" in t and team):
        # On préférera TODAY si on est le jour J, sinon LAST
        # Le service décidera.
        return {"intent": "SPORT_RESULT_TODAY", "team": team}

    return {}
