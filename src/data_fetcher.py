import sqlite3
import requests
import time

DATABASE_NAME = "bazaar_history.db"


def initialize_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS bazaar_updates
                     (
                         update_id INTEGER PRIMARY KEY AUTOINCREMENT,
                         timestamp INTEGER,
                         product_id TEXT,
                         buy_price REAL,
                         sell_price REAL,
                         buy_volume INTEGER,
                         sell_volume INTEGER
                     )
                     """)


def fetch_and_store():
    url = "https://api.hypixel.net/v2/skyblock/bazaar"
    response = requests.get(url)
    if response.status_code != 200:
        return

    data = response.json()
    last_updated = data['lastUpdated']


    # PM NOTE: You could add a check here to see if last_updated
    # matches the last entry in your DB to skip redundant writes.



    rows_to_insert = []
    for product_id, info in data['products'].items():
        status = info['quick_status']
        rows_to_insert.append((
            last_updated,
            product_id,
            status['buyPrice'],
            status['sellPrice'],
            status['buyVolume'],
            status['sellVolume']
        ))

    # Efficient Bulk Insert
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.executemany("""
                         INSERT INTO bazaar_updates
                             (timestamp, product_id, buy_price, sell_price, buy_volume, sell_volume)
                         VALUES (?, ?, ?, ?, ?, ?)
                         """, rows_to_insert)

    print(f"Logged {len(rows_to_insert)} items at {last_updated}")


if __name__ == "__main__":
    initialize_db()
    while True:
        fetch_and_store()
        time.sleep(60)