from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

from intent_detector import detect_intent
from response_generator import generate_response

app = Flask(__name__)

with open("memoire_mohamed_lanai.json", "r", encoding="utf-8") as f:
    data_mohamed = json.load(f)

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
    app.run(debug=True)
