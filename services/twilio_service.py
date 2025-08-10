from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, TWILIO_WHATSAPP_TO

_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def _fmt(n: str) -> str:
    return n if n.startswith("whatsapp:") else f"whatsapp:{n}"

def send_whatsapp_safe(text: str) -> bool:
    """Envoie via l'API Twilio. Retourne True si envoyé, False si bloqué (quota, etc.)."""
    try:
        _client.messages.create(
            from_=_fmt(TWILIO_WHATSAPP_FROM),
            to=_fmt(TWILIO_WHATSAPP_TO),
            body=text
        )
        return True
    except TwilioRestException as e:
        # On ne casse rien si quota/limite → on log juste False
        if getattr(e, "status", None) in (429, 400) or "limit" in str(e).lower() or "quota" in str(e).lower():
            print("[Lanai] Limite Twilio atteinte. Message non envoyé (mais app OK).")
            return False
        raise
