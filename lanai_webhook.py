# lanai_webhook.py
import os
import traceback
from flask import Flask, request, jsonify

app = Flask(__name__)

# --------- IMPORTS AVEC SÉCURITÉ ---------
BOOT_ERRORS = {}

def _record_boot_error(name: str, err: Exception):
    BOOT_ERRORS[name] = f"{type(err).__name__}: {err}"
    traceback.print_exc()

try:
    from services.twilio_service import send_whatsapp_safe
    TWILIO_OK = True
except Exception as e:
    _record_boot_error("services.twilio_service", e)
    TWILIO_OK = False
    def send_whatsapp_safe(_text: str) -> bool:
        print("[Lanai][WARN] Twilio non chargé, envoi ignoré.")
        return False

try:
    from lanai_core.router import handle_message as _router_handle
    ROUTER_OK = True
except Exception as e:
    _record_boot_error("lanai_core.router", e)
    ROUTER_OK = False
    def _router_handle(text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ["bonjour","salut","hello","hi"]):
            return "Salut Mohamed 😊 Ça va aujourd’hui ?"
        if "météo" in t or "meteo" in t:
            return "Je regarde la météo et je te dis bientôt 🙂"
        if "match" in t or "nba" in t or "foot" in t:
            return "Je prépare les résultats des matchs, une minute."
        if "souvenir" in t:
            return "Tu te rappelles d’un bon moment en famille ?"
        if "lana" in t:
            return "Une caresse pour Lana 🐱"
        return "Bien reçu. Je suis là si tu veux parler."

handle_message = _router_handle

# --------- HEALTH & ADMIN ---------
@app.route("/", methods=["GET", "HEAD"])   # <-- FIX: pas de @app.head()
def root():
    return "Lanai OK", 200

@app.get("/admin/health")
def admin_health():
    from config import (
        TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
        OPENWEATHER_API_KEY, OPENAI_API_KEY,
        APP_TIMEZONE, PROFILE_JSON_PATH
    )
    return jsonify({
        "ok": True,
        "imports": {
            "router": ROUTER_OK,
            "twilio_service": TWILIO_OK,
            "boot_errors": BOOT_ERRORS
        },
        "env": {
            "twilio_keys": bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN),
            "openweather": bool(OPENWEATHER_API_KEY),
            "openai": bool(OPENAI_API_KEY),
            "timezone": APP_TIMEZONE,
            "profile_path": PROFILE_JSON_PATH
        }
    }), 200

# --------- WEBHOOK TWILIO (REST) ---------
@app.post("/whatsapp")
def whatsapp_webhook():
    try:
        incoming = (request.form.get("Body") or "").strip()
    except Exception:
        incoming = ""

    try:
        reply = handle_message(incoming)
    except Exception:
        traceback.print_exc()
        reply = "Je n’ai pas tout compris, mais je suis là pour toi."

    sent = False
    try:
        sent = send_whatsapp_safe(reply)  # True si envoyé (quota ok), False sinon
    except Exception:
        traceback.print_exc()

    app.logger.info(f"[Lanai] inbound='{incoming}' -> reply_sent={sent}")
    return ("", 204)

# --------- LOG AU DÉMARRAGE ---------
@app.before_first_request
def _boot_log():
    try:
        from config import (
            APISPORTS_KEY_BASKET, APISPORTS_KEY_FOOT,
            OPENWEATHER_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
        )
        print(
            "[Lanai] BOOT => "
            f"BASKET={'OK' if APISPORTS_KEY_BASKET else 'NO'} | "
            f"FOOT={'OK' if APISPORTS_KEY_FOOT else 'NO'} | "
            f"WEATHER={'OK' if OPENWEATHER_API_KEY else 'NO'} | "
            f"TWILIO={'OK' if (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN) else 'NO'}"
        )
        if BOOT_ERRORS:
            print("[Lanai][WARN] Boot errors:", BOOT_ERRORS)
    except Exception as e:
        print("[Lanai][WARN] Boot log error:", repr(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=False)
