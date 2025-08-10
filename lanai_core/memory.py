import json
from config import PROFILE_JSON_PATH

def load_memory() -> dict:
    try:
        with open(PROFILE_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

MEMORY = load_memory()

def get_default_city(mem: dict) -> str:
    return (
        mem.get("city_default")
        or mem.get("profile", {}).get("city_default")
        or "Loffre"
    )
