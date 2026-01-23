import pandas as pd
import numpy as np
from data_eda import get_product_data, get_info, get_all_data


def calculate_rolling_sharpe(df, window=30):
    df['net_profit'] = df['buy_price'] - df['sell_price'] #add tax multiplier to buy price

    rolling_mean = df['net_profit'].rolling(window=window).mean()
    rolling_std = df['net_profit'].rolling(window=window).std()

    df['rolling_sharpe'] = rolling_mean / rolling_std
    return df

def trades_per_hour(df, window=60):
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

    potential_volume = min(hourly_buy_velocity, hourly_sell_velocity)
    return potential_volume


def profit_per_hour(df, window=60):
    last_row = df.iloc[-1]
    #add tax to buy_price
    margin = last_row["buy_price"] - last_row["sell_price"]

    profit = trades_per_hour(df, window) * margin
    return profit

# print(profit_per_hour(get_product_data("AUTO_SMELTER")))

def get_market_velocity(df_history, window=60):

    if len(df_history) > window:
        df_window = df_history.iloc[-(window + 1):].copy()
    else:
        df_window = df_history.copy()

    pivot_vol = df_window.pivot(index='timestamp', columns='product_id', values='buy_moving_week')
    vol_delta = pivot_vol.iloc[-1] - pivot_vol.iloc[0]
    vol_delta = vol_delta.clip(lower=0)

    actual_duration_hrs = (pivot_vol.index[-1] - pivot_vol.index[0]) / 3600
    hourly_velocity = vol_delta / actual_duration_hrs

    print(df_history)
    print(df_window)
    print(pivot_vol)
    print(vol_delta)
    print(actual_duration_hrs)


    return hourly_velocity

get_market_velocity(get_all_data())

# def top_flips():
#     df = get_all_data()
#     tax_rate = 0.98875
#
#     latest = df.sort_values('timestamp').groupby('product_id').tail(1).copy()
#     latest['profit_per_unit'] = (latest['buy_price'] * tax_rate) - latest['sell_price']
#
#     latest['profit_per_hour'] = latest['profit_per_unit'] * trades_per_hour(latest['product_id'])
#
#     filtered = latest[latest['profit_per_unit'] > 0]
#     top_10 = filtered.sort_values(by='profit_per_hour', ascending=False).head(10)
#
#     return top_10

def top_flips():
    # Get current snapshots
    df = get_all_data()

    latest = df.sort_values('timestamp').groupby('product_id').tail(1).copy()

    # Get velocities
    velocities = get_market_velocity(window_minutes=60)

    # Merge velocity onto latest prices
    # This is like a SQL JOIN on product_id
    df = latest.join(velocities, on='product_id')

    # Apply Tax (1.125% total = 0.98875)
    tax_rate = 0.98875
    df['profit_per_unit'] = (df['buy_price'] * tax_rate) - df['sell_price']

    # Calculate Final Metric
    df['potential_profit_hr'] = df['profit_per_unit'] * df['hourly_velocity']

    # Filter for realistic items (e.g., must have at least 10 trades per hour)
    filtered = df[
        (df['profit_per_unit'] > 0) &
        (df['hourly_velocity'] > 10)
        ]

    return filtered.sort_values(by='potential_profit_hr', ascending=False).head(10)

# top_flips()



