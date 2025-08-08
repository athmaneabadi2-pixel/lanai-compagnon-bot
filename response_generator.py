from utils_api import get_next_psg_match
from openai import OpenAI
import os

client_ai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_response(intent, user_msg: str, data_json: dict):
    # INTENT = toujours un dict maintenant !
    if intent["intent"] == "football":
        return get_next_psg_match(os.environ.get("API_FOOT_KEY"))
    
    elif intent["intent"] == "general":
        # Réponses personnalisées pour Mohamed !
        msg_lower = user_msg.lower()
        if "bonjour" in msg_lower:
            return "Bonjour Mohamed ! 😊 Comment puis-je t’aider aujourd’hui ?"
        elif "ça va" in msg_lower or "ca va" in msg_lower:
            return "Je vais bien, merci ! Et toi, comment tu te sens aujourd’hui ?"
        elif "salut" in msg_lower:
            return "Salut Mohamed ! Je suis là si tu veux discuter."
        else:
            return "Tu veux parler de foot, de basket, de météo ou d'autre chose ? 😊"
        
    # Ajoute ici tes autres intents (basketball, weather, etc.)
    # Exemple :
    # elif intent["intent"] == "basketball":
    #     ...

    else:
        return "Je réfléchis encore à une réponse !"

