# --- Shim de compatibilité pour le webhook WhatsApp ---
# Permet: from services.weather_service import weather_text

import os
import requests
from config import OPENWEATHER_API_KEY

# Villes supportées (ajoute si besoin)
KNOWN_CITIES = {
    "loffre": {"lat": 50.3844, "lon": 3.1069, "label": "Loffre"},
    "le cannet": {"lat": 43.5769, "lon": 7.0191, "label": "Le Cannet"},
}

def _pick_city(name: str, default_city: str = "Loffre"):
    if not name:
        name = default_city
    n = (name or "").strip().lower()
    if "cannet" in n:
        return KNOWN_CITIES["le cannet"]
    if "loffre" in n:
        return KNOWN_CITIES["loffre"]
    # fallback: par défaut
    return KNOWN_CITIES.get(default_city.strip().lower(), KNOWN_CITIES["loffre"])

def _onecall(lat: float, lon: float) -> dict:
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat, "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric", "lang": "fr",
    }
    r = requests.get(url, params=params, timeout=12)
    r.raise_for_status()
    return r.json()

def weather_text(when: str | None = None, city: str | None = None, default_city: str = "Loffre") -> str:
    """
    Retourne un petit texte météo pour aujourd'hui/demain.
    when: "today" | "demain" | "tomorrow" | None
    city: ex. "Loffre", "Le Cannet"
    """
    if not OPENWEATHER_API_KEY:
        return "Clé OpenWeather manquante."

    choice = _pick_city(city, default_city=default_city)
    data = _onecall(choice["lat"], choice["lon"])
    daily = data.get("daily", [])
    if not daily:
        return "Impossible de récupérer la météo."

    # index 0 = aujourd'hui, 1 = demain
    idx = 0
    if when and when.lower() in ("demain", "tomorrow"):
        idx = 1 if len(daily) > 1 else 0

    d = daily[idx]
    tmin = round(d["temp"]["min"])
    tmax = round(d["temp"]["max"])
    desc = (d["weather"][0]["description"] or "").capitalize()
    jour = "Aujourd'hui" if idx == 0 else "Demain"
    ville = choice["label"]

    return f"{jour} à {ville}: {tmin}–{tmax}°C. {desc}."
