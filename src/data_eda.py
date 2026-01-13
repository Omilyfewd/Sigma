import sqlite3
import pandas as pd
import numpy as np

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




def get_info(item, window=0):
    df = get_product_data(item)

    assert(window >= 0, "bruh")
    if window:
        df = df.rolling(window)

    summary = df[['buy_price', 'buy_volume', 'sell_price', 'buy_volume']].describe()
    print(type(summary))
    print(summary)
    return summary



get_info('ENCHANTED_GOLD')

def returns(df):
    df['log_returns'] = np.log(df['buy_price'] / df['buy_price'].shift(1))


#check for
    results = df['timestamp'].apply(valid_entry, args=(df['timestamp'] .shift(1),)).dropna()
    valid = results.all()



def valid_entry(curr, prev):
    return curr < prev + 90000

sum = get_info('ENCHANTED_GOLD')
mean_b_iloc = sum.iloc[0, 0]

print(mean_b_iloc)