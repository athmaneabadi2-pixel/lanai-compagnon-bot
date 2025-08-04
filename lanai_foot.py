import requests
from datetime import datetime, timedelta

# Clé d'API et paramètres
api_key = "80d51b2c0dmsh5e929daece8dcfdp14d63ejsnb2397421a3f9"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# Calcul de la date d'hier
hier = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
# Compétitions ciblées (ID à filtrer)
competitions = {
    "Ligue 1": 61,
    "Premier League": 39,
    "Bundesliga": 78,
    "Serie A": 135,
    "La Liga": 140,
    "Ligue des Champions": 2,
    "Europa League": 3,
    "Conférence League": 848,
    "France (nation)": 1,     # à vérifier
    "Algérie (nation)": 26    # à vérifier
}

# Appel pour chaque ligue
for nom, id_ligue in competitions.items():
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?date={hier}&league={id_ligue}&season=2024"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        matchs = response.json().get('response', [])
        for match in matchs:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            score_home = match['goals']['home']
            score_away = match['goals']['away']
            print(f"[{nom}] {home} {score_home} - {score_away} {away}")
    else:
        print(f"Erreur pour {nom} : {response.status_code}")






