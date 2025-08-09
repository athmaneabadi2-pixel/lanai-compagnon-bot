from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json, os

from intent_detector import detect_intent_gpt as detect_intent
from response_generator import generate_response

app = Flask(__name__)

def load_profile():
    raw = os.environ.get("USER_PROFILE_JSON")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    try:
        with open("memoire_mohamed_lanai.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

PROFILE = load_profile()

@app.route("/webhook", methods=["POST"])
def webhook():
    user_msg = request.form.get("Body", "") or ""
    intent = detect_intent(user_msg)
    try:
        reply = generate_response(intent, user_msg, PROFILE)
    except Exception as e:
        print("ERREUR generate_response:", repr(e))
        reply = "Désolé, un petit souci technique. On réessaie dans une minute."
    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
