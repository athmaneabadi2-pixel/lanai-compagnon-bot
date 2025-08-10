import os

# === Twilio ===
TWILIO_ACCOUNT_SID     = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN      = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM   = os.getenv("TWILIO_WHATSAPP_NUMBER")   # ton nom
TWILIO_WHATSAPP_TO     = os.getenv("MY_WHATSAPP_NUMBER")       # ton nom

# === APIs Sports ===
APISPORTS_KEY_BASKET   = os.getenv("API_BASKET_KEY")           # ton nom
APISPORTS_KEY_FOOT     = os.getenv("API_FOOT_KEY")             # ton nom

# === OpenWeather ===
OPENWEATHER_API_KEY    = os.getenv("OPENWEATHER_API_KEY")      # ton nom

# === OpenAI (optionnel V1)
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY")           # ton nom

# === App ===
APP_TIMEZONE           = os.getenv("APP_TIMEZONE", "Europe/Paris")
PROFILE_JSON_PATH      = os.getenv("PROFILE_JSON_PATH", "memoire_mohamed_lanai.json")
APP_JOBS_SECRET        = os.getenv("APP_JOBS_SECRET")
