import datetime, pytz
from flask import Flask, request, abort
from twilio.twiml.messaging_response import MessagingResponse

from config import APP_TIMEZONE
from lanai_core.router import route
from lanai_core.memory import MEMORY, get_default_city
from lanai_core.services.weather_service import get_forecast
from lanai_core.services.sports_service import sports_dispatch
from lanai_core.services.openai_service import reply_gpt

TZ = pytz.timezone(APP_TIMEZONE)
app = Flask(__name__)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/whatsapp")
def whatsapp_webhook():
    body = (request.form.get("Body") or "").strip()
    if not body:
        abort(400)

    args = route(body)
    intent = args["intent"]

    try:
        if intent == "WEATHER":
            text = get_forecast(args.get("city"), args.get("when", "aujourdhui"), get_default_city(MEMORY))
        elif intent == "DATE":
            now = datetime.datetime.now(TZ)
            text = now.strftime("Nous sommes le %d/%m/%Y, il est %H:%M.")
        elif intent == "MEMORY":
            q = (args.get("query") or "").lower()
            prof = MEMORY.get("profile", {})
            if "enfant" in q and MEMORY.get("children"):
                text = "Tes enfants: " + ", ".join(MEMORY["children"])
            elif any(w in q for w in ["femme", "épouse"]) and prof.get("spouse"):
                text = f"Ta femme: {prof['spouse']}."
            else:
                souvenirs = MEMORY.get("souvenirs") or prof.get("souvenirs") or []
                text = f"Souvenir: {souvenirs[0]}" if souvenirs else "Je garde tes souvenirs en tête. Tu veux m’en raconter un ?"
        elif intent.startswith("SPORT_"):
            text = sports_dispatch(intent, args.get("sport"), args.get("team"), args.get("date_hint"))
        elif intent == "SMALLTALK":
            text = "Je suis là si tu veux parler. 💬"
        else:
            text = reply_gpt(body, MEMORY)
    except Exception as e:
        text = f"Désolé, j’ai eu un souci technique. ({type(e).__name__})"

    resp = MessagingResponse()
    resp.message(text)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
