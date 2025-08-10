# lanai_webhook.py
import os
from flask import Flask, request
from lanai_core.router import handle_message
from services.twilio_service import send_whatsapp_safe

app = Flask(__name__)

@app.get("/")
def health():
    return "Lanai OK", 200

# Webhook WhatsApp (REST) : on calcule la réponse et on l'envoie via l'API Twilio
@app.post("/whatsapp")
def whatsapp_webhook():
    incoming = (request.form.get("Body") or "").strip()
    reply = handle_message(incoming)
    sent = send_whatsapp_safe(reply)  # True si envoyé, False si (quota...) – on ignore le quota ici
    app.logger.info(f"[Lanai] inbound='{incoming}' -> sent={sent}")
    return ("", 204)  # Twilio OK (on ne renvoie pas de TwiML)
