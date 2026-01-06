import requests
import sqlite3
import time
import json
import os
from pathlib import Path

def get_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

api = "https://api.hypixel.net/v2/skyblock/bazaar"

con = sqlite3.connect('data.db')
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS product_data
                   (productId PRIMARY KEY,
                    sellPrice,
                    sellVolume,
                    sellMovingWeek,
                    sellOrders,
                    buyPrice,
                    buyVolume,
                    buyMovingWeek,
                    buyOrders
                    )
            """)


def fetch_time_and_products():
    data = get_data(api)

    if data and data['success']:
        last_updated = data['lastUpdated']
        bazaar_products = data['products']

    return last_updated, bazaar_products

previous_time = -1
while True:
    if fetch_time_and_products()[0] != previous_time:

        rows = []

        for product in fetch_time_and_products()[1]:
            row = list(fetch_time_and_products()[1][product]['quick_status'].values())
            rows.append(row)

        cur.executemany(
            "INSERT INTO product_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows
        )
        con.commit()

        previous_time = fetch_time_and_products()[0]

        time.sleep(60)




# res = cur.execute("SELECT buyVolume FROM product_data")
# res.fetchone()

# print(type(res))
# print(type(res.fetchall()))
# print(len(res.fetchall()))









# BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_DIR = BASE_DIR / "data"
#
#
#
#

# def save(response_json):
#     if response_json is None:
#         return
#
#     DATA_DIR.mkdir(parents=True, exist_ok=True)
#
#     file_path = DATA_DIR / "bazaarData.json"
#
#     with open(file_path, 'w') as outfile:
#         json.dump(response_json, outfile, indent=4)
#
#     print(f"Successfully saved data to: {file_path}")
#
#     return file_path
#
#
#
#
# data = get_data(url)
# path = save(data)
#
#
# def load():
#     with open(path, 'r') as infile:
#         data_dict = json.load(infile)
#     return data_dict

