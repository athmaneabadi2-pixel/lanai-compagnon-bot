import requests
import os

# Clé API depuis Render (à ajouter dans "Environment Variables" sous le nom OPENWEATHER_API_KEY)
api_key = os.environ.get("OPENWEATHER_API_KEY")

if not api_key:
    raise ValueError("❌ Clé API météo manquante. Ajoutez OPENWEATHER_API_KEY dans Render.")

# Codes postaux ou noms de villes
villes = {
    "Loffre (Mohamed & Milouda)": "Loffre,FR",
    "Le Cannet (où vit Yacine)": "Le Cannet,FR"
}

# Fonction pour récupérer la météo
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = round(data["main"]["temp"])
        description = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        return f"{temp}°C, {description}, humidité {humidity}%"
    else:
        return f"Impossible de récupérer la météo pour {city}"

# Création du message
print("📅 Météo du jour :\n")
for nom, ville in villes.items():
    meteo = get_weather(ville)
    print(f"🌍 {nom} : {meteo}")
