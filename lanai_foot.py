import requests
import os
from datetime import datetime, timedelta

# Date d'hier
hier = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# Clés API depuis Render
api_foot_key = os.environ.get("API_FOOT_KEY")
api_basket_key = os.environ.get("API_BASKET_KEY")

# Headers Foot
headers_foot = {
    "X-RapidAPI-Key": api_foot_key,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# Headers Basket
headers_basket = {
    "X-RapidAPI-Key": api_basket_key,
    "X-RapidAPI-Host": "api-basketball.p.rapidapi.com"
}

# ⚽ COMPÉTITIONS DE FOOT
competitions_foot = {
    "Ligue 1": 61,
    "Ligue des Champions": 2,
    "France (nation)": 1
}

# 🏀 COMPÉTITIONS DE BASKET
competitions_basket = {
    "NBA": 12,
    "LNB Pro A": 87
}

# Stocker tous les résultats trouvés
resultats = []

# FOOT
for nom, id_ligue in competitions_foot.items():
    try:
        url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?date={hier}&league={id_ligue}&season=2024"
        response = requests.get(url, headers=headers_foot)
        if response.status_code == 200:
            matchs = response.json().get('response', [])
            for match in matchs:
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                score_home = match['goals']['home']
                score_away = match['goals']['away']
                resultats.append(f"[{nom}] {home} {score_home} - {score_away} {away}")
    except:
        pass

# BASKET
for nom, id_league in competitions_basket.items():
    try:
        url = f"https://api-basketball.p.rapidapi.com/games?date={hier}&league={id_league}&season=2024"
        response = requests.get(url, headers=headers_basket)
        if response.status_code == 200:
            matchs = response.json().get("response", [])
            for match in matchs:
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                score_home = match['scores']['home']['points']
                score_away = match['scores']['away']['points']
                resultats.append(f"[{nom}] {home} {score_home} - {score_away} {away}")
    except:
        pass

# Afficher uniquement s'il y a des résultats
if resultats:
    print(f"📊 Résultats du {hier}")
    for ligne in resultats:
        print(ligne)
