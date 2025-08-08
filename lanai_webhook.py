from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

from intent_detector import detect_intent_gpt as detect_intent
from response_generator import generate_response

app = Flask(__name__)

# Chargement mémoire Mohamed (gère l’erreur si fichier absent)
try:
    with open("memoire_mohamed_lanai.json", "r", encoding="utf-8") as f:
        data_mohamed = json.load(f)
except FileNotFoundError:
    data_mohamed = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    user_msg = request.form.get("Body", "")
    intent = detect_intent(user_msg)
    try:
        reply = generate_response(intent, user_msg, data_mohamed)
    except Exception as e:
        reply = "Désolé, une erreur technique empêche Lanai de répondre."

    response = MessagingResponse()
    response.message(reply)
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

