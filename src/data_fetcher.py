import requests
import json
import os
from pathlib import Path

url = "https://api.hypixel.net/v2/skyblock/bazaar"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def get_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def save(response_json):
    if response_json is None:
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / "bazaarData.json"

    with open(file_path, 'w') as outfile:
        json.dump(response_json, outfile, indent=4)

    print(f"Successfully saved data to: {file_path}")


data = get_data(url)
save(data)