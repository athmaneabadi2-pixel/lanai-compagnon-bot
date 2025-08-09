import os, json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def detect_intent_gpt(message: str):
    prompt = f"""
Tu analyses un message WhatsApp et tu renvoies uniquement un JSON valide:

{{
  "intent": "football" | "basketball" | "weather" | "general",
  "team": string | null,
  "player": string | null,
  "action": "score" | "next_match" | "calendar" | "ranking" | "injury_status" | "current_weather" | null,
  "date": string | null
}}

Exemples:
- "C'est quand le prochain match du PSG ?" =>
{{"intent":"football","team":"PSG","player":null,"action":"next_match","date":null}}
- "Score du RC Lens hier" =>
{{"intent":"football","team":"RC Lens","player":null,"action":"score","date":"hier"}}
- "Les Lakers jouent quand ?" =>
{{"intent":"basketball","team":"Los Angeles Lakers","player":null,"action":"next_match","date":null}}
- "Météo à Paris demain" =>
{{"intent":"weather","team":null,"player":null,"action":"current_weather","date":"demain"}}
- "Salut ça va ?" =>
{{"intent":"general","team":null,"player":null,"action":null,"date":null}}

Message:
« {message} »
Réponds UNIQUEMENT par le JSON demandé.
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200,
        )
        content = resp.choices[0].message.content.strip()
        return json.loads(content)
    except Exception:
        # Sécurité: valeur par défaut
        return {"intent": "general", "team": None, "player": None, "action": None, "date": None}
