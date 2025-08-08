import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def detect_intent_gpt(message):
    prompt = f"""
Tu es une IA experte qui analyse les messages WhatsApp pour détecter l'intention de l'utilisateur concernant le football, le basket ou la météo, ou une question générale.
Tu peux détecter :
- Le sport concerné (football, basketball, weather, general)
- L’équipe (team) ou le joueur (player)
- L’action demandée (score, calendrier, prochain match, classement, blessure, actualité, météo…)
- Une date précise si mentionnée (ex : "hier", "aujourd'hui", "demain", "14 août", etc.)

Réponds **exclusivement** en JSON, jamais de texte libre.

Structure du JSON :
{{
  "intent": "football" ou "basketball" ou "weather" ou "general",
  "team": "nom de l’équipe si concerné, sinon null",
  "player": "nom du joueur si question sur un joueur, sinon null",
  "action": "score" ou "next_match" ou "calendar" ou "ranking" ou "injury_status" ou "current_weather" ou "news" ou null,
  "date": "date précise ou indication comme 'hier', 'aujourd’hui', 'demain', sinon null"
}}

Exemples :

- "C'est quand le prochain match du PSG ?" =>
{{
  "intent": "football",
  "team": "PSG",
  "player": null,
  "action": "next_match",
  "date": null
}}

- "Score du RC Lens hier" =>
{{
  "intent": "football",
  "team": "RC Lens",
  "player": null,
  "action": "score",
  "date": "hier"
}}

- "Le calendrier de Lyon" =>
{{
  "intent": "football",
  "team": "Lyon",
  "player": null,
  "action": "calendar",
  "date": null
}}

- "Mbappé est blessé ?" =>
{{
  "intent": "football",
  "team": null,
  "player": "Mbappé",
  "action": "injury_status",
  "date": null
}}

- "Résultat du match de l’Algérie du 12 juillet" =>
{{
  "intent": "football",
  "team": "Algérie",
  "player": null,
  "action": "score",
  "date": "12 juillet"
}}

- "Classement de la Ligue 1" =>
{{
  "intent": "football",
  "team": null,
  "player": null,
  "action": "ranking",
  "date": null
}}

- "C’est quoi la météo à Paris demain ?" =>
{{
  "intent": "weather",
  "team": null,
  "player": null,
  "action": "current_weather",
  "date": "demain"
}}

- "Les prochains matchs de Boston Celtics" =>
{{
  "intent": "basketball",
  "team": "Boston Celtics",
  "player": null,
  "action": "calendar",
  "date": null
}}

- "Est-ce que LeBron James joue ce soir ?" =>
{{
  "intent": "basketball",
  "team": null,
  "player": "LeBron James",
  "action": "injury_status",
  "date": "ce soir"
}}

- "Salut, comment tu vas ?" =>
{{
  "intent": "general",
  "team": null,
  "player": null,
  "action": null,
  "date": null
}}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300
    )
    json_response = response.choices[0].message.content.strip()
    try:
        return json.loads(json_response)
    except Exception:
        # En cas d’erreur, retourne une intention "générale" basique
        return {
            "intent": "general",
            "team": None,
            "player": None,
            "action": None,
            "date": None
        }
