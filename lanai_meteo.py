import requests
import os

# Clé API depuis Render (à ajouter dans "Environment Variables" sous le nom OPENWEATHER_API_KEY)
api_key = os.getenv("OPENWEATHER_API_KEY")

if not api_key:
    raise ValueError("❌ Clé API météo manquante. Ajoutez OPENWEATHER_API_KEY dans Render.")

# Villes avec noms de villes
villes = {
    "Loffre (Mohamed & Milouda)": "Loffre,FR",
    "Le Cannet (où Yacine vit)": "Le Cannet,FR"
}

# Fonction pour récupérer la météo
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = round(data["main"]["temp"])
            description = data["weather"][0]["description"].capitalize()
            humidity = data["main"]["humidity"]
            return f"{temp}°C, {description}, humidité {humidity}%"
        else:
            return f"❌ Erreur {response.status_code} pour {city}"
    except Exception as e:
        return f"⚠️ Erreur : {e}"

# Création du message
print("📍 Météo du jour :\n")
for nom, ville in villes.items():
    meteo = get_weather(ville)
    print(f"🌤 {nom} : {meteo}")
