from utils_api import get_next_psg_match
from openai import OpenAI
import os

client_ai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_response(intent, user_msg: str, data_json: dict):
    # INTENT est toujours un dictionnaire

    # Exemple pour le foot (à adapter pour d'autres cas)
    if intent["intent"] == "football":
        # Appelle ta fonction foot ou renvoie une phrase, selon ton besoin
        return get_next_psg_match(os.environ.get("API_FOOT_KEY"))
    
    # Ajoute ici basket, météo, etc.
    # elif intent["intent"] == "basketball":
    #     return ...

    # Si aucune intention précise ("general" ou tout ce qui n'est pas reconnu)
    else:
        # Réponse directe via GPT-4 avec une consigne adaptée à Mohamed
        response = client_ai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es Lanai, un compagnon WhatsApp bienveillant pour Mohamed Djeziri. "
                        "Mohamed est âgé, il a la maladie de Parkinson, tu fais attention à être clair, chaleureux, sans jargon, en phrases courtes. "
                        "Sa femme s'appelle Milouda, son chat Lana. Tu donnes des conseils simples, tu réponds toujours avec humanité. "
                        "Si la question est sur la santé, donne des conseils généraux, jamais de diagnostic médical. "
                        "Ne dis jamais que tu es une IA. Si tu connais des souvenirs ou infos sur Mohamed, glisse-les naturellement."
                    )
                },
                {
                    "role": "user",
                    "content": user_msg
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
