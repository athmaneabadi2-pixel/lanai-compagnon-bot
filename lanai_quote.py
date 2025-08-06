import os
from openai import OpenAI
from twilio.rest import Client

# ==== Variables d'environnement (Render) ====
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")  # ex: "whatsapp:+14155238886"
MY_WHATSAPP_NUMBER = os.environ.get("MY_WHATSAPP_NUMBER")  # ex: "whatsapp:+33XXXXXXXXX"

# ==== Vérifications ====
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY manquant dans Render.")
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("❌ Clés Twilio manquantes dans Render.")
if not TWILIO_WHATSAPP_NUMBER or not MY_WHATSAPP_NUMBER:
    raise ValueError("❌ Numéros WhatsApp Twilio/Moi manquants dans Render.")

# ==== Initialisation ====
client_ai = OpenAI(api_key=OPENAI_API_KEY)
client_twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ==== Prompt amélioré ====
prompt = """
Donne-moi un hadith authentique en français avec :
1. Le texte du hadith
2. Une courte explication claire (max 30 mots)
3. Mention de la source (ex : Sahih al-Bukhari)
Réponds de façon concise et bien structurée.
"""

try:
    # ==== Génération du hadith ====
    response = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un assistant qui partage des hadiths authentiques avec explications simples."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=120
    )

    quote = response.choices[0].message.content.strip()
    print(f"🌟 Hadith du jour :\n{quote}")

    # ==== Envoi via WhatsApp ====
    message = client_twilio.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=MY_WHATSAPP_NUMBER,
        body=f"🌟 Hadith du jour 🌟\n\n{quote}"
    )

    print("✅ Message WhatsApp envoyé :", message.sid)

except Exception as e:
    print(f"Erreur : {e}")
