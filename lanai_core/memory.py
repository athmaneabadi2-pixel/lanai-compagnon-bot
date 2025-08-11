import json
from config import PROFILE_JSON_PATH

def load_memory() -> dict:
    try:
        with open(PROFILE_JSON_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return {}

    # Normalisation du JSON de profil (sections FR)
    profile = {}
    fam = raw.get("Famille", {})
    ident = raw.get("Identité", {})
    vie = raw.get("Vie quotidienne", {})

    profile["name"] = ident.get("Nom complet") or (f'{ident.get("Prénom", "")} {ident.get("Nom", "")}'.strip() or "Mohamed Djeziri")
    profile["spouse"] = fam.get("Épouse") or fam.get("Epouse") or fam.get("Nom de son épouse") or "Milouda"
    children_val = fam.get("Enfants") or fam.get("Nom(s) et âge(s) des enfants")
    if isinstance(children_val, str):
        # Extraire les prénoms des enfants depuis la chaîne (en ignorant les âges)
        names = []
        for part in children_val.split(","):
            name = part.split("(")[0].strip()
            if name:
                names.append(name)
        profile["children"] = names
    else:
        profile["children"] = children_val or []
    profile["pet"] = vie.get("Animal de compagnie") or "Lana"

    # Traitement des petits-enfants (extraction des prénoms)
    grandkids_val = fam.get("Petits-enfants (noms, âges, relation)") or fam.get("Petits-enfants")
    if isinstance(grandkids_val, str):
        # Extraire les prénoms des petits-enfants depuis la chaîne (ignore les détails)
        gnames = []
        for part in grandkids_val.split(","):
            subpart = part.split("–")[0].strip()
            name = subpart.split("(")[0].strip()
            if name:
                gnames.append(name)
        profile["grandchildren"] = gnames
    else:
        profile["grandchildren"] = grandkids_val or []

    profile["city_default"] = raw.get("Ville par défaut") or "Loffre"

    return {"_raw": raw, "profile": profile}

# Charger la mémoire au démarrage
MEMORY = load_memory()

def get_default_city(mem: dict) -> str:
    return mem.get("profile", {}).get("city_default") or "Loffre"
