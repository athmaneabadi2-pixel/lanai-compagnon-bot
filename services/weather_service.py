# services/weather_service.py
import requests
import pytz
from config import OPENWEATHER_API_KEY, APP_TIMEZONE

TZ = pytz.timezone(APP_TIMEZONE)

# Ajoute/édite les villes ici si besoin
KNOWN_CITIES = {
    "Loffre": {"lat": 50.3844, "lon": 3.1069},
    "Le Cannet": {"lat": 43.5769, "lon": 7.0191},
}

def _onecall(lat: float, lon: float, lang="fr"):
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": lang}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def get_forecast(city: str | None, when: str, default_city: str) -> str:
    """
    city: nom de ville optionnel (str ou None)
    when: "aujourdhui" ou "demain"
    default_city: ville par défaut (depuis le JSON mémoire)
    """
    name = (city or default_city or "Loffre").title()
    coords = KNOWN_CITIES.get(name)
    if not coords:
        name = (default_city or "Loffre").title()
        coords = KNOWN_CITIES.get(name, KNOWN_CITIES["Loffre"])

    data = _onecall(coords["lat"], coords["lon"])
    d = data["daily"][1] if when == "demain" else data["daily"][0]
    tmin, tmax = round(d["temp"]["min"]), round(d["temp"]["max"])
    desc = d["weather"][0]["description"].capitalize()
    jour = "Demain" if when == "demain" else "Aujourd'hui"
    return f"{jour} à {name}: {tmax}°/{tmin}°. {desc}."
