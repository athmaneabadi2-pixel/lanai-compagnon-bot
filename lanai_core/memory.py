import json
from config import PROFILE_JSON_PATH

def load_memory() -> dict:
    try:
        with open(PROFILE_JSON_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return {}

    # --- Normalisation depuis ton JSON actuel ---
    profile = {}
    fam = raw.get("Famille", {})
    ident = raw.get("Identité", {})

    profile["spouse"]   = fam.get("Épouse") or fam.get("Epouse") or "Milouda"
    profile["children"] = fam.get("Enfants") or []
    profile["pet"]      = raw.get("Vie quotidienne", {}).get("Animal de compagnie", "Lana")
    profile["city_default"] = raw.get("Ville par défaut") or "Loffre"

    # On garde l’original aussi
    return {"_raw": raw, "profile": profile}

MEMORY = load_memory()

def get_default_city(mem: dict) -> str:
    return (
        mem.get("profile", {}).get("city_default")
        or "Loffre"
    )
