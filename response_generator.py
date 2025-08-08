from utils_api import get_next_psg_match
from openai import OpenAI
import os

client_ai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_response(intent: str, user_msg: str, data_json: dict):
    if intent == "football":
        return get_next_psg_match(os.environ.get("API_FOOT_KEY"))
    elif intent == "general":
        prompt = f"""Tu es Lanai, un assistant bienveillant qui parle à Mohamed. Voici son message : « {user_msg} »\nTu connais ses infos : {data_json}. Réponds naturellement."""
        response = client_ai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    else:
        return "Je réfléchis encore à une réponse !"
