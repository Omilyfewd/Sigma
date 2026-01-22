import pandas as pd
import numpy as np
from data_eda import get_product_data, get_info


def calculate_rolling_sharpe(df, window=30):
    df['net_profit'] = df['buy_price'] - df['sell_price'] #add tax multiplier to buy price

    rolling_mean = df['net_profit'].rolling(window=window).mean()
    rolling_std = df['net_profit'].rolling(window=window).std()

    df['rolling_sharpe'] = rolling_mean / rolling_std
    return df


def profit_per_hour(df, window=60):
    if len(df) > window:
        subset = df.iloc[-(window + 1):].copy()
    else:
        subset = df.copy()

    subset['buy_delta'] = subset['buy_moving_week'].diff()
    subset['sell_delta'] = subset['sell_moving_week'].diff()

    buy_vol = subset[subset['buy_delta'] > 0]['buy_delta'].sum()
    sell_vol = subset[subset['sell_delta'] > 0]['sell_delta'].sum()

    start_time = subset.index[0]
    end_time = subset.index[-1]
    duration_hours = (end_time - start_time) / 3600000

    if duration_hours <= 0:
        return 0

    hourly_buy_velocity = buy_vol / duration_hours
    hourly_sell_velocity = sell_vol / duration_hours

    # 5. Calculate Profit
    last_row = df.iloc[-1]
    # Note: Ensure you account for tax (approx 1% to 1.125%)
    # Gross Margin = Instabuy_Price (Sell Offer) - Instasell_Price (Buy Order)
    # Based on your data columns: buy_price is likely the higher value (Instabuy)
    margin = last_row["buy_price"] - last_row["sell_price"]


    print(buy_vol)
    print(sell_vol)
    print(duration_hours)
    print(hourly_buy_velocity)
    print(hourly_sell_velocity)
    print(margin)

    profit = min(hourly_buy_velocity, hourly_sell_velocity) * margin
    return profit

print(profit_per_hour(get_product_data("BOOSTER_COOKIE")))