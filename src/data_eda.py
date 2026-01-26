import os
import sqlite3

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "bazaar.db")

def get_product_data(product_id):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM bazaar_updates_2 WHERE product_id = ? ORDER BY timestamp ASC"

    try:
        df = pd.read_sql_query(query, con, params=(product_id,))
    finally:
        con.close()

    return df

def get_all_data():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM bazaar_updates_2 ORDER BY timestamp ASC"

    try:
        df = pd.read_sql_query(query, con)
    finally:
        con.close()

    return df


def get_recent_data(window_minutes=60):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)

    buffer_minutes = 5
    ms_to_look_back = (window_minutes + buffer_minutes) * 60 * 1000

    query = """
            SELECT * \
            FROM bazaar_updates_2
            WHERE timestamp >= (SELECT MAX(timestamp) \
                                FROM bazaar_updates_2) - ?
            ORDER BY product_id, timestamp
            """

    try:
        df = pd.read_sql_query(query, con, params=(ms_to_look_back,))
    finally:
        con.close()

    return df

def get_info(df, window=0):
    assert window < 0, "bruh"
    if window:
        df = df.rolling(window)

    summary = df[['buy_price', 'buy_volume', 'sell_price', 'buy_volume', 'buy_moving_week', 'sell_moving_week']].describe()
    print(type(summary))
    print(summary)
    return summary
