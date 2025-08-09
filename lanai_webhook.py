# lanai_webhook.py
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

from intent_detector import detect_intent_gpt as detect_intent
from response_generator import generate_response

app = Flask(__name__)

# Charger la "mémoire" de Mohamed (optionnel)
try:
    with open("memoire_mohamed_lanai.json", "r", encoding="utf-8") as f:
        data_mohamed = json.load(f)
except FileNotFoundError:
    data_mohamed = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    user_msg = request.form.get("Body", "")
    intent = detect_intent(user_msg)
    print("INTENT DÉTECTÉ:", intent)  # visible dans les logs Render
    try:
        reply = generate_response(intent, user_msg, data_mohamed)
    except Exception as e:
        print("ERREUR generate_response:", e)
        reply = "Désolé, une erreur technique empêche Lanai de répondre."
    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
