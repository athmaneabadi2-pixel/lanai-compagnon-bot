import requests
from config import OPENWEATHER_API_KEY

def _geo(city: str):
    url = "https://api.openweathermap.org/geo/1.0/direct"
    r = requests.get(url, params={"q": city, "limit": 1, "appid": OPENWEATHER_API_KEY}, timeout=15)
    r.raise_for_status()
    arr = r.json()
    if not arr: return None
    return arr[0]["lat"], arr[0]["lon"]

def weather_tomorrow_short(city: str = "Paris") -> str:
    if not OPENWEATHER_API_KEY:
        return "Météo indisponible (clé manquante)."
    loc = _geo(city) or (48.8566, 2.3522)
    lat, lon = loc
    url = "https://api.openweathermap.org/data/3.0/onecall"
    r = requests.get(url, params={
        "lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY,
        "units": "metric", "lang": "fr", "exclude": "minutely,hourly,current,alerts"
    }, timeout=20)
    if r.status_code != 200:
        return "Météo indisponible pour le moment."
    data = r.json()
    daily = data.get("daily", [])
    if len(daily) < 2:
        return "Météo indisponible."
    d = daily[1]  # demain
    tmax = round(d["temp"]["max"])
    tmin = round(d["temp"]["min"])
    desc = d["weather"][0]["description"].capitalize()
    return f"Demain: {tmax}°/{tmin}°. {desc}."
