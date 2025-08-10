# lanai_webhook.py
import os
from flask import Flask, request
from twilio.rest import Client

app = Flask(__name__)

# ==== ENV ====
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.environ.get("TWILIO_WHATSAPP_FROM") or os.environ.get("TWILIO_WHATSAPP_NUMBER")
TO_NUMBER   = os.environ.get("TWILIO_WHATSAPP_TO")   or os.environ.get("MY_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp(text: str):
    if not (FROM_NUMBER and TO_NUMBER):
        print("[Lanai] FROM/TO WhatsApp manquants")
        return
    client.messages.create(from_=f"whatsapp:{FROM_NUMBER.split(':')[-1]}" if "whatsapp:" not in FROM_NUMBER else FROM_NUMBER,
                           to=f"whatsapp:{TO_NUMBER.split(':')[-1]}" if "whatsapp:" not in TO_NUMBER else TO_NUMBER,
                           body=text)

@app.get("/")
def health():
    return "Lanai OK", 200

@app.post("/whatsapp")
def whatsapp_webhook():
    body = (request.form.get("Body") or "").strip().lower()
    # Réponses ultra simples pour valider le flux
    if body in ("bonjour","salut","hello","hi"):
        send_whatsapp("Salut Mohamed 😊 Comment ça va aujourd’hui ?")
    elif "météo" in body:
        send_whatsapp("Météo: je regarde et je te dis ! (version test)")
    elif "match" in body:
        send_whatsapp("Pour les matchs, je te prépare un petit résumé. (version test)")
    elif "souvenir" in body:
        send_whatsapp("Tu te rappelles de ta médaille d’arbitrage sous la télé ? 🎖️")
    else:
        send_whatsapp("Bien reçu. Je suis là si tu veux parler.")
    return ("", 204)

if __name__ == "__main__":
    # Render injecte $PORT
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=False)
