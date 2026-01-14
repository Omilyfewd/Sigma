import sqlite3
import pandas as pd

def get_product_data(product_id):
    con = sqlite3.connect('../data/bazaar.db')
    query = "SELECT * FROM bazaar_updates_2 WHERE product_id = ? ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, con, params=(product_id,))
    con.close()

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def get_all_data():
    con = sqlite3.connect('../data/bazaar.db')
    query = "SELECT * FROM bazaar_updates_2 ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, con)
    con.close()

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def get_info(df, window=0):
    assert window >= 0, "bruh"
    if window:
        df = df.rolling(window)

    summary = df[['buy_price', 'buy_volume', 'sell_price', 'buy_volume', 'buy_moving_week', 'sell_moving_week']].describe()
    print(type(summary))
    print(summary)
    return summary

pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.10f' % x)
print(get_product_data("ENCHANTED_GOLD")[['buy_moving_week', 'sell_moving_week']])

