import sqlite3
import pandas as pd


def get_product_data(product_id):
    con = sqlite3.connect('../data/bazaar.db')
    query = "SELECT * FROM bazaar_updates WHERE product_id = ? ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, con, params=(product_id,))
    con.close()

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def get_all_data():
    con = sqlite3.connect('../data/bazaar.db')
    query = "SELECT * FROM bazaar_updates ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, con)
    con.close()

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df




def get_info(item):
    df = get_product_data(item)
    summary = df[['buy_price', 'buy_volume', 'sell_price', 'buy_volume']].describe()
    print(summary)
    return summary


