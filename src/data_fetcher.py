import sqlite3
import requests
import time

DATABASE_NAME = "bazaar_history.db"
def initialize_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS bazaar_updates_with_index
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
        conn.execute("""CREATE INDEX IF NOT EXISTS idx_product_time 
            ON bazaar_updates (product_id, timestamp)""")


def fetch_and_store():
    url = "https://api.hypixel.net/v2/skyblock/bazaar"
    response = requests.get(url)
    if response.status_code != 200:
        return

    data = response.json()
    last_updated = data['lastUpdated']

    #Add here matches to time entries to prevent writing data if no time has passed

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
        time.sleep(60) # data stored in bazaar updates:
        #23:45 - 00:38 from 1/05/26


