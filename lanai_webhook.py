import os
import datetime
import pytz
from flask import Flask, request, abort
from twilio.twiml.messaging_response import MessagingResponse

from config import APP_TIMEZONE
from lanai_core.router import route  # tu gardes ton routeur actuel
from lanai_core.memory import MEMORY, get_default_city
from lanai_core.memory_qa import answer_memory_query
from services.weather_service import weather_text  # ta fonction existante qui marche
from services.sports_service import sports_dispatch
from services.openai_service import reply_gpt

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def handle_whatsapp():
    if request.method != "POST":
        abort(405)

    body = (request.form.get("Body") or "").strip()

    try:
        r = route(body)
        intent = r.get("intent")

        if intent == "METEO":
            when = r.get("when")
            city = r.get("city") or get_default_city(MEMORY)
            text = weather_text(when=when, city=city, default_city=get_default_city(MEMORY))

        elif intent and intent.startswith("SPORT"):
            text = sports_dispatch(
                intent=intent,
                sport=r.get("sport"),
                team=r.get("team"),
                date_hint=r.get("date_hint"),
            )

        elif intent == "DATE":
            tz = pytz.timezone(APP_TIMEZONE)
            now = datetime.datetime.now(tz)
            text = f"Nous sommes le {now.strftime('%d/%m/%Y')}, il est {now.strftime('%H:%M')}."

        elif intent == "MEMORY":
            ans = answer_memory_query(body, MEMORY)
            text = ans or "Tu veux me raconter un souvenir ? 😊"

        elif intent == "SMALLTALK":
            text = "Bonjour 😊 Je suis là si tu veux parler."

        else:
            # fallback GPT
            text = reply_gpt(body, MEMORY)

    except Exception as e:
        print(f"[Lanai] Error: {e.__class__.__name__}: {e}")
        text = "Désolé, j’ai eu un souci technique."

    resp = MessagingResponse()
    resp.message(text)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
