import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from data_eda import get_product_data, get_all_data, get_info


def price_trend(product_id):
    df = get_product_data(product_id)

    df['moving_avg'] = df['buy_price'].rolling(window=10).mean()

    plt.figure(figsize=(12, 6))

    # Plotting multiple lines
    plt.plot(df.index, df['buy_price'], label='Buy Price', color='green', alpha=0.6)
    plt.plot(df.index, df['sell_price'], label='Sell Price', color='red', alpha=0.6)
    plt.plot(df.index, df['moving_avg'], label='10-min MA', color='blue', linestyle='--')

    # Adding labels (Professional touch)
    plt.ticklabel_format(style='plain', axis='y') #NOTE

    plt.title(f'{" ".join([word.lower().capitalize() for word in product_id.split("_")])}: Price Trend Over Time', fontsize=14)
    plt.xlabel('Time')
    plt.ylabel('Coins')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)

    plt.show()

def spread(product_id):
    # df = get_product_data(product_id)
    df = get_all_data()

    # Calculate spread with the 1.25% tax logic we found in your source code
    df['net_spread'] = (df['buy_price'] * 0.9875) - df['sell_price']

    plt.figure(figsize=(10, 5))

    #df = df[(df['net_spread'] > -10000) & (df['net_spread'] < 100000)]

    #plt.ticklabel_format(style='plain', axis='x') #NOTE
    plt.hist(df['net_spread'].dropna(), bins=30, color='skyblue', edgecolor='black')

    # Add a vertical line for the mean
    plt.axvline(df['net_spread'].mean(), color='red', linestyle='dashed', linewidth=1, label='Mean Spread')

    plt.title('Distribution of Net Profit per Flip')
    plt.xlabel('Profit (Coins)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()

def scatter(product_id):
    df = get_product_data(product_id)

    df.plot.scatter(x='buy_volume', y='buy_price')  # Use c for color mapping
    plt.show()

def rolling_volatility(product_id):
    df = get_product_data(product_id)

    df['moving_std_hour'] = df['buy_price'].rolling(window=60).std()
    if get_info(product_id).iloc[0, 0] < 1440:
        mu = df['buy_price'].mean()
    else:
        mu = df['buy_price'].rolling(window=1440).mean()
    df['z_score'] = (df['buy_price'] - mu) / df['moving_std_hour']

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['z_score'], label='Buy Price z score')
    plt.show()

# scatter("ENCHANTED_GOLD")
rolling_volatility("ENCHANTED_GOLD")