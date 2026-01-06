import requests

def fetch_data():
    url = "https://api.hypixel.net/v2/skyblock/bazaar"
    response = requests.get(url)
    if response.status_code != 200:
        return

    data = response.json()
    last_updated = data['lastUpdated']

    return data, last_updated


# Current data stored in bazaar updates: 23:45 - 00:38 from 1/05/26


