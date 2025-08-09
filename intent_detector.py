# intent_detector.py
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def detect_intent_gpt(message: str):
    prompt = f"""
Tu analyses un message WhatsApp et tu renvoies l'intention en JSON uniquement.

JSON attendu :
{{
  "intent": "football" | "basketball" | "weather" | "general",
  "team": string | null,
  "player": string | null,
  "action": "score" | "next_match" | "calendar" | "ranking" | "injury_status" | "current_weather" | null,
  "date": string | null
}}

Exemples :
- "C'est quand le prochain match du PSG ?" =>
{{"intent":"football","team":"PSG","player":null,"action":"next_match","date":null}}
- "Score du RC Lens hier" =>
{{"intent":"football","team":"RC Lens","player":null,"action":"score","date":"hier"}}
- "Le calendrier de Lyon" =>
{{"intent":"football","team":"Lyon","player":null,"action":"calendar","date":null}}
- "Les Lakers jouent quand ?" =>
{{"intent":"basketball","team":"Los Angeles Lakers","player":null,"action":"next_match","date":null}}
- "Météo à Paris demain" =>
{{"intent":"weather","team":null,"player":null,"action":"current_weather","date":"demain"}}
- "Salut ça va ?" =>
{{"intent":"general","team":null,"player":null,"action":null,"date":null}}

Message :
« {message} »
"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300,
    )
    content = resp.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except Exception:
        return {"intent": "general", "team": None, "player": None, "action": None, "date": None}
