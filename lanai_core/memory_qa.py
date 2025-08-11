def answer_memory_query(user_text: str, memory: dict) -> str | None:
    t = (user_text or "").lower()
    profile = (memory or {}).get("profile", {})

    if "petit" in t and "enfant" in t:
        grandkids = profile.get("grandchildren") or []
        if grandkids:
            return "Tes petits-enfants : " + ", ".join(grandkids) + "."
        return "Je n’ai pas cette information pour l’instant."

    if "enfant" in t or "fils" in t or "fille" in t:
        kids = profile.get("children") or []
        if kids:
            return "Tes enfants : " + ", ".join(kids) + "."
        return "Je n’ai pas cette information pour l’instant."

    if "femme" in t or "épouse" in t or "epouse" in t:
        return f"Ta femme s’appelle {profile.get('spouse', 'Milouda')}."

    if "chat" in t or "animal" in t:
        return f"Ton chat s’appelle {profile.get('pet', 'Lana')}."

    if "je m'appelle" in t or "mon nom" in t or "comment je m'appelle" in t:
        first_name = (profile.get("name", "Mohamed Djeziri") or "Mohamed").split()[0]
        return f"Tu t’appelles {first_name}. C’est un joli prénom ! Comment ça va aujourd’hui ?"

    return None
