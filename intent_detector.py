import os
import requests

API_FOOT_KEY = os.environ.get("API_FOOT_KEY")
BASE_URL = "https://v3.football.api-sports.io"

# Petite base d'ID équipe (à compléter !)
TEAM_IDS = {
    "PSG": 85,
    "Paris SG": 85,
    "Paris": 85,
    "OM": 81,
    "Marseille": 81,
    "Lyon": 80,
    "RC Lens": 116,
    "Lens": 116,
    "Monaco": 91,
    # Ajoute les autres clubs ici !
}

def get_next_match(team_name):
    team_id = TEAM_IDS.get(team_name)
    if not team_id:
        return f"Désolé, je ne trouve pas l'équipe '{team_name}' dans ma base de données."
    url = f"{BASE_URL}/fixtures?team={team_id}&next=1"
    headers = {"x-apisports-key": API_FOOT_KEY}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data["response"]:
            match = data['response'][0]
            date = match['fixture']['date'][:10]
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            return f"Le prochain match du {team_name} : {home} vs {away}, le {date}."
        else:
            return "Pas de prochain match trouvé."
    else:
        return "Impossible de récupérer le prochain match."

def generate_response(intent, user_msg, data_json):
    # ROUTING SPORT
    if intent["intent"] == "football":
        if intent.get("action") == "next_match" and intent.get("team"):
            return get_next_match(intent["team"])
        # ICI tu ajoutes d'autres actions comme score, calendrier, joueur...
        # elif intent.get("action") == "score":
        #    return get_score(intent["team"], intent.get("date"))
        else:
            return "Tu veux parler de foot ? Peux-tu préciser ta question (équipe, date, joueur…) ?"
    # ROUTING AUTRES SPORTS
    elif intent["intent"] == "basketball":
        # Si tu as une API basket, même logique ici !
        return "Fonction basket à ajouter ici !"
    # ROUTING COMPAGNON (GPT)
    else:
        return generate_gpt_response(user_msg, data_json)  # Ta fonction actuelle GPT-4 compagnon

# Exemple de fonction GPT compagnon (existant chez toi)
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_gpt_response(user_msg, data_json):
    prompt = f"""
Tu es Lanai, l’ami bienveillant de Mohamed. Tu connais ses infos : {data_json}.
Réponds toujours simplement, chaleureusement, en français facile.
Voici le message : « {user_msg} »
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()
