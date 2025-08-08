import requests

def get_next_psg_match(api_key: str):
    url = "https://api.sportmonks.com/v3/football/fixtures?filter[team]=14&sort=starting_at&api_token=" + api_key
    response = requests.get(url)
    data = response.json()
    try:
        match = data['data'][0]
        return f"Prochain match du PSG contre {match['participants'][1]['name']}, le {match['starting_at'][:10]} à {match['starting_at'][11:16]}."
    except:
        return "Impossible de trouver le prochain match du PSG."
