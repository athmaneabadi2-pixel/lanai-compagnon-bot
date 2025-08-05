import requests
import os
from datetime import datetime, timedelta

# Clé API depuis Render (ajouter dans "Environment Variables" sous le nom OPENWEATHER_API_KEY)
api_key = os.environ.get("OPENWEATHER_API_KEY")

if not api_key:
    raise ValueError("❌ Clé API météo manquante. Ajoutez OPENWEATHER_API_KEY dans Render.")

# Coordonnées GPS des villes
villes = {
    "Loffre": {"lat": 50.3844, "lon": 3.1069},        # Loffre
    "Le Cannet (où Yacine vit)": {"lat": 43.5769, "lon": 7.0191}  # Le Cannet
}

# Fonction pour récupérer la météo de demain
def get_weather_tomorrow(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # "daily" = prévisions journalières, index [1] = demain
        tomorrow_data = data["daily"][1]
        
        temp = round(tomorrow_data["temp"]["day"])
        description = tomorrow_data["weather"][0]["description"].capitalize()
        humidity = tomorrow_data["humidity"]
        
        return f"{temp}°C, {description}, humidité {humidity}%"
    else:
        return "Impossible de récupérer la météo"

# Date de demain
tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

# Message personnalisé pour Mohamed
print(f"🤲 Salam aleykum Mohamed, voici la météo de demain ({tomorrow_date}) :\n")
for nom, coords in villes.items():
    meteo = get_weather_tomorrow(coords["lat"], coords["lon"])
    print(f"🌤 {nom} : {meteo}")
