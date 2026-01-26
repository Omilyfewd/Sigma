import numpy as np
import matplotlib.pyplot as plt

from analysis import calculate_market_velocity, get_top_flips, margin_sharpe
from data_eda import get_product_data, get_recent_data


def price_trend(df, product_id):
    df['moving_avg'] = df['buy_price'].rolling(window=10).mean()

    plt.figure(figsize=(12, 6))

    plt.plot(df.index, df['buy_price'], label='Buy Price', color='green', alpha=0.6)
    plt.plot(df.index, df['sell_price'], label='Sell Price', color='red', alpha=0.6)
    plt.plot(df.index, df['moving_avg'], label='10-min MA', color='blue', linestyle='--')

    plt.ticklabel_format(style='plain', axis='y') #NOTE

    #Super cool formatting >:)
    plt.title(f'{" ".join([word.lower().capitalize() for word in product_id.split("_")])}: Price Trend Over Time', fontsize=14)
    plt.xlabel('Time')
    plt.ylabel('Coins')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)

    plt.show()


# price_trend(get_product_data("ENCHANTED_GOLD"), "ENCHANTED_GOLD")

def spread(df):
    tax_rate = 0.9875
    df['net_spread'] = (df['buy_price'] * tax_rate) - df['sell_price']

    plt.figure(figsize=(10, 5))

    #df = df[(df['net_spread'] > -10000) & (df['net_spread'] < 100000)]

    #plt.ticklabel_format(style='plain', axis='x') #NOTE
    plt.hist(df['net_spread'].dropna(), bins=30, color='skyblue', edgecolor='black')
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
    df['micro_price'] = (
                                (df['buy_price'] * df['sell_volume']) + (df['sell_price'] * df['buy_volume'])
                        ) / (df['buy_volume'] + df['sell_volume'])

    df['returns'] = np.log(df['micro_price'] / df['micro_price'].shift(1))

    rolling_return = df['returns'].rolling(window=window).mean()
    df['rolling_returns'] = rolling_return
    rolling_volatility = df['returns'].rolling(window=window).std()

    epsilon = 1e-9 #no divide by 0
    df['rolling_sharpe'] = rolling_return / (rolling_volatility + epsilon)
    df['profit_index'] = df['rolling_sharpe'] * np.sqrt(window)

    plt.plot(df.index, df['rolling_returns'], label='returns', color='green', alpha=0.6)
    plt.show()

    return df



# dataFrame = get_product_data("ENCHANTED_IRON_BLOCK")
# calculate_metrics(dataFrame)

def pph_distribution():
    data = get_recent_data()
    df = get_top_flips(calculate_market_velocity(data), data, 100)

    plt.hist(df['projected_pph'].dropna(), bins=30, color='skyblue', edgecolor='black')
    plt.show()

pph_distribution()


def visualize_sharpe_and_pph(product_id, window_hours=12):
    tax_rate = 0.98875
    # recent = get_recent_data(window_hours * 60)

    recent = get_product_data(product_id)

    recent['net_margin'] = (recent['buy_price'] * tax_rate) - recent['sell_price']

    stats = recent.groupby('product_id')['net_margin'].agg(['mean', 'std'])
    stats['margin_sharpe'] = stats['mean'] / (stats['std'] + 1e-9)

    print(stats)

    plt.hist(recent['net_margin'].dropna(), bins=30, color='skyblue', edgecolor='black')

    # plt.hist(stats['margin_sharpe'].dropna(), bins=30, color='green', edgecolor='black')

    plt.show()

    plt.plot(recent.index, recent['buy_price'], label='Buy Price', color='green', alpha=0.6)
    plt.plot(recent.index, recent['sell_price'], label='Sell Price', color='red', alpha=0.6)

    plt.show()

    data = get_recent_data()
    get_top_flips(calculate_market_velocity(data), recent, 1835)


    return stats[['margin_sharpe']]

visualize_sharpe_and_pph("RECOMBOBULATOR_3000", 12)
