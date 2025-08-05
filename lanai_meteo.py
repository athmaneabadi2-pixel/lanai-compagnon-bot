import requests
import os
from datetime import datetime, timedelta

# Clé API météo depuis Render
api_key = os.environ.get("OPENWEATHER_API_KEY")

if not api_key:
    raise ValueError("❌ Clé API météo manquante. Ajoutez OPENWEATHER_API_KEY dans Render.")

# Coordonnées GPS précises
villes = {
    "Loffre": {"lat": 50.3844, "lon": 3.1069},        
    "Le Cannet (où Yacine vit)": {"lat": 43.5769, "lon": 7.0191}
}

# Récupérer la météo de demain avec One Call 3.0
def get_weather_tomorrow(lat, lon):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Impossible de récupérer la météo (code {response.status_code})"

    data = response.json()

    if "daily" not in data:
        return "Impossible de trouver la météo de demain (pas de données 'daily')"

    # Demain = index 1
    tomorrow_data = data["daily"][1]
    temp = round(tomorrow_data["temp"]["day"])
    description = tomorrow_data["weather"][0]["description"].capitalize()
    humidity = tomorrow_data["humidity"]

    return f"{temp}°C, {description}, humidité {humidity}%"

# Date de demain
tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

# Message
print(f"🤲 Salam aleykum Mohamed, voici la météo de demain ({tomorrow_date}) :\n")
for nom, coords in villes.items():
    meteo = get_weather_tomorrow(coords["lat"], coords["lon"])
    print(f"🌤 {nom} : {meteo}")
