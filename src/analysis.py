import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from data_eda import get_all_data, get_recent_data


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

def volume_derivative(df):
    # df = df.sort_values(['product_id', 'timestamp'])

    df['buy_delta'] = df.groupby('product_id')['buy_moving_week'].diff()
    df['sell_delta'] = df.groupby('product_id')['sell_moving_week'].diff()

    df['buy_delta'] = df['buy_delta'].clip(lower=0)
    df['sell_delta'] = df['sell_delta'].clip(lower=0)

    df[['buy_delta', 'sell_delta']] = df[['buy_delta', 'sell_delta']].fillna(0)

    return df

def calculate_market_velocity(df, window_minutes=60) -> pd.DataFrame:
    processed_df = volume_derivative(df)

    latest_time = processed_df['timestamp'].max()
    window_start = latest_time - ((window_minutes + 0.1) * 60000)
    recent_df = processed_df[processed_df['timestamp'] >= window_start]

    velocity = recent_df.groupby('product_id').agg(
        total_buy=('buy_delta', 'sum'),
        total_sell=('sell_delta', 'sum'),
        duration_hrs=('timestamp', lambda x: (x.max() - x.min()) / 3600000)
    )

    velocity['hourly_vol'] = np.minimum(velocity['total_buy'], velocity['total_sell']) / velocity['duration_hrs']

    return velocity

# calculate_market_velocity(get_all_data())


def get_top_flips(velo_df, df, top_n=10):
    latest_prices = df.drop_duplicates('product_id', keep='last')
    latest_prices = latest_prices[['product_id', 'buy_price', 'sell_price']]

    merged = velo_df.merge(latest_prices, left_index=True, right_on='product_id')

    tax_rate = 0.9875
    merged['margin'] = (merged['buy_price'] * tax_rate) - merged['sell_price']

    merged['projected_pph'] = merged['margin'] * merged['hourly_vol']
    valid_flips = merged[
        (merged['margin'] > 0) &
        (merged['hourly_vol'] > 10)  # Adjust here
        ]

    top_flips = valid_flips.sort_values('projected_pph', ascending=False).head(top_n)

    pd.set_option('display.float_format', '{:,.6f}'.format)
    pd.set_option('display.max_columns', None)

    # print(top_flips[["product_id", "buy_price", "sell_price", "margin", "hourly_vol", "projected_pph"]])

    return top_flips

# data = get_recent_data()
# get_top_flips(calculate_market_velocity(data), data)



#calculate sharpe ratios for each flip using all data/data over last 12h(or all data if less than 12)
#calculate sharpes for all items, stability in margins
#merge top flips and sharpes df
#decide how to determine best flips, as sharpes and pph are different metrics relative, and cannot be compared directly.
#method 1: find top 10% of sharpes and return top flips from that list
#method 2: return highest sharpe * pph values, rebalanced to some metric.


def margin_sharpe(recent): #needs full df(12+ hour)
    tax_rate = 0.98875

    recent['net_margin'] = (recent['buy_price'] * tax_rate) - recent['sell_price']

    stats = recent.groupby('product_id')['net_margin'].agg(['mean', 'std'])
    stats['margin_sharpe'] = stats['mean'] / (stats['std'] + 1e-9)

    return stats[['margin_sharpe', 'mean', 'std']]


def merged_data(window_hours=12):
    full_df = get_all_data()
    recent_df = get_recent_data(window_hours * 60)

    top_flips = get_top_flips(calculate_market_velocity(recent_df), recent_df, 1836)
    sharpe_data = margin_sharpe(full_df)
    merged = top_flips.join(sharpe_data, on='product_id')

    return merged

def risk_adjusted_pph_log(df): #takes merged data
    df['logged_sharpes'] = np.log1p(df['margin_sharpe'])
    df['risk_adjusted_pph'] = df['projected_pph'] * df['logged_sharpes']

    pd.set_option('display.max_columns', None)

    # df = df[df['product_id'] = ""]
    print(df[['product_id', 'buy_price', 'sell_price', 'margin', 'mean', 'std', 'hourly_vol', 'projected_pph', 'margin_sharpe', 'logged_sharpes', 'risk_adjusted_pph']].sort_values(by='projected_pph', ascending=False))


    print("\n Data Frame Columns: \n", df.columns)

    return df



def filtering(df, cap):
    '''
    Because skyblock is incredibly diverse, sharp ratios change drastically and some stuff r stale in comparison
    1. increase min volume threshold, 100
    2. effective_std = max(real_std, mean_price * 0.01), items not moving are prob not good to buy
    3. Cap sharpe ratios above 5 as they are basically the same.
    4. Normalize 0 - 1
    '''
    df['margin_sharpe'] = df['margin_sharpe'].clip(upper=cap)
    df['logged_pph'] = np.log1p(df['projected_pph'])

    s_min, s_max = df['margin_sharpe'].min(), df['margin_sharpe'].max()
    p_min, p_max = df['logged_pph'].min(), df['logged_pph'].max()

    df['norm_sharpe'] = (df['margin_sharpe'] - s_min) / (s_max - s_min)
    df['norm_pph'] = (df['logged_pph'] - p_min) / (p_max - p_min)

    df['alpha_score'] = (df['norm_pph'] * 0.7) + (df['norm_sharpe'] * 0.3)

    print(df[['product_id', 'buy_price', 'sell_price', 'margin',
              'mean', 'std', 'hourly_vol', 'projected_pph',
              'margin_sharpe', 'norm_sharpe', 'norm_pph',
              'alpha_score']].sort_values(by='buy_price', ascending=False))


    return df.sort_values('alpha_score', ascending=False)

risk_adjusted_pph_log(merged_data())
filtering(merged_data(), 5)











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

# def top_flips():
#     df = get_all_data()
#
#     latest = df.sort_values('timestamp').groupby('product_id').tail(1).copy()
#
#     velocities = get_market_velocity(window_minutes=60)
#     df = latest.join(velocities, on='product_id')
#
#     tax_rate = 0.98875
#     df['profit_per_unit'] = (df['buy_price'] * tax_rate) - df['sell_price']
#
#     df['potential_profit_hr'] = df['profit_per_unit'] * df['hourly_velocity']
#
#     filtered = df[
#         (df['profit_per_unit'] > 0) &
#         (df['hourly_velocity'] > 10)
#         ]
#
#     return filtered.sort_values(by='potential_profit_hr', ascending=False).head(10)

# top_flips()



