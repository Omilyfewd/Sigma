import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_eda import get_product_data, get_all_data, get_info


def price_trend(df, product_id):
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

def spread(df):
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

def scatter(df):
    df.plot.scatter(x='buy_volume', y='buy_price')  # Use c for color mapping
    plt.show()


def calculate_metrics(df, window=30):
    """
    df requires: buyPrice, sellPrice, buyVolume, sellVolume
    window: number of periods (minutes) for the rolling calculation
    """

    df['micro_price'] = (
                                (df['buy_price'] * df['sell_volume']) + (df['sell_price'] * df['buy_volume'])
                        ) / (df['buy_volume'] + df['sell_volume'])

    # 2. Calculate Log Returns of the Micro-Price
    df['returns'] = np.log(df['micro_price'] / df['micro_price'].shift(1))

    # 3. Rolling Sharpe Ratio
    # Formula: (Mean Return - Risk Free) / Std Dev
    # We assume Risk-Free Rate = 0 for the Bazaar
    rolling_return = df['returns'].rolling(window=window).mean()
    df['rolling_returns'] = rolling_return
    rolling_volatility = df['returns'].rolling(window=window).std()

    # Add epsilon to volatility to avoid 'Infinity' Sharpe Ratios
    epsilon = 1e-9
    df['rolling_sharpe'] = rolling_return / (rolling_volatility + epsilon)

    # 4. Annualizing (Optional, but good for practice)
    # Since Bazaar is 24/7, 'annual' is just scaling by sqrt of time
    # To 'Minutize' for your project:
    # Let's call it 'Profitability Index'
    df['profit_index'] = df['rolling_sharpe'] * np.sqrt(window)

    plt.plot(df.index, df['rolling_returns'], label='returns', color='green', alpha=0.6)
    plt.show()

    return df



dataFrame = get_product_data("ENCHANTED_IRON_BLOCK")
calculate_metrics(dataFrame)