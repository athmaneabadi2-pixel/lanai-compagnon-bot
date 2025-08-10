def answer_memory_query(user_text: str, memory: dict) -> str | None:
    t = (user_text or "").lower()
    profile = (memory or {}).get("profile", {})

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
        return f"Tu t’appelles {profile.get('name', 'Mohamed Djeziri')}."

    return None
