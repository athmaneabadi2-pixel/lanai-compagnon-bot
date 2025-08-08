import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def detect_intent_gpt(message):
    prompt = f"""
Tu es une IA qui analyse les messages WhatsApp pour détecter ce que veut savoir un utilisateur.

Voici le message : « {message} »

Réponds uniquement en JSON, jamais de texte libre.

Structure :
{{
  "intent": "football" ou "basketball" ou "weather" ou "general",
  "team": "nom d’équipe si foot ou basket, sinon null",
  "action": "next_match" ou "current_weather" ou null
}}

Exemples :
- "C'est quand le prochain match du PSG ?" =>
{{"intent": "football", "team": "PSG", "action": "next_match"}}

- "Il fait beau à Paris ?" =>
{{"intent": "weather", "team": null, "action": "current_weather"}}

- "Donne-moi le prochain match de l'OM" =>
{{"intent": "football", "team": "OM", "action": "next_match"}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=200
    )
    json_response = response.choices[0].message.content.strip()
    try:
        return json.loads(json_response)
    except Exception:
        # Optionnel : retour basique si la réponse GPT est mal formatée
        return {
            "intent": "general",
            "team": None,
            "action": None
        }


