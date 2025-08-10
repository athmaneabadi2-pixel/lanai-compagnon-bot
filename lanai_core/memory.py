import json
from config import PROFILE_JSON_PATH

def load_profile() -> dict:
    try:
        with open(PROFILE_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
