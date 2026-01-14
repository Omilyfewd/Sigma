import pandas as pd
from data_eda import get_product_data, get_info


def calculate_rolling_sharpe(df, window=30):
    df['net_profit'] = df['buy_price'] - df['sell_price'] #add tax multiplier to buy price

    rolling_mean = df['net_profit'].rolling(window=window).mean()
    rolling_std = df['net_profit'].rolling(window=window).std()

    df['rolling_sharpe'] = rolling_mean / rolling_std
    return df

def profit_per_hour(df, window=60):
    last_row = df.iloc[-1]

    buy = last_row.loc["buy_price"]
    sell = last_row.loc["sell_price"]

    margin = buy - sell

    # items = window if get_info(df).iloc[0, 0] >= window else get_info(df).iloc[0, 0]

    avg_buy_velocity, avg_sell_velocity = 0, 0
    bought, sold = 0, 0
    cur_buy_moving, cur_sell_moving = 0, 0

    count = 1
    for _, row in df.iterrows():

    # for i in range(1, items + 1):
    #     row = next(it)
        if row["buy_moving_week"] > cur_buy_moving:
            bought += row["buy_moving_week"] - cur_buy_moving
            avg_buy_velocity = bought / count
            cur_buy_moving = row["buy_moving_week"]
        else:
            bought += avg_buy_velocity
            avg_buy_velocity = bought / count
            cur_buy_moving = row["buy_moving_week"]

        if row["sell_moving_week"] > cur_sell_moving:
            sold += row["sell_moving_week"] - cur_sell_moving
            avg_sell_velocity = sold / count
            cur_sell_moving = row["sell_moving_week"]
        else:
            sold += avg_sell_velocity
            avg_sell_velocity = sold / count
            cur_sell_moving = row["sell_moving_week"]

        if count >= window + 1:
            break
        else:
            count += 1

    insta_buy_per_period = avg_buy_velocity
    insta_sell_per_period = avg_sell_velocity

    profit = min(insta_buy_per_period, insta_sell_per_period) * margin
    return profit


print(profit_per_hour(get_product_data("ENCHANTED_GOLD")))