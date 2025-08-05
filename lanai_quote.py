import os
from openai import OpenAI

# Variables d'environnement (Render)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Vérification
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY manquant dans Render.")

# Initialisation OpenAI
client_ai = OpenAI(api_key=OPENAI_API_KEY)

# Prompt amélioré
prompt = """
Donne-moi un hadith authentique en français avec :
1. Le texte du hadith
2. Une courte explication claire (max 30 mots)
3. Mention de la source (ex : Sahih al-Bukhari)
Réponds de façon concise et bien structurée.
"""

try:
    response = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un assistant qui partage des hadiths authentiques avec explications simples."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=120
    )

    quote = response.choices[0].message.content.strip()
    print(f"🌟 Hadith du jour :\n{quote}")

except Exception as e:
    print(f"Erreur OpenAI : {e}")
