import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analysis import merged_data, filtering
from data_eda import get_recent_data

st.set_page_config(page_title="Sigma Bazaar Quant", layout="wide")
st.title("📈 Quantitative trading and market analysis tool")

@st.cache_data(ttl=60)
def load_processed_data():
    raw_merged = merged_data(window_hours=12)
    return filtering(raw_merged, cap=5)

df = load_processed_data()

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Market Leaderboard", "Item Drill-down"])

if page == "Market Leaderboard":
    st.subheader("Top Risk-Adjusted Flips (Alpha Score)")
    st.write("Ranked by a 70/30 split of Projected PPH and Normalized Sharpe Ratio.")

    top_df = df[['product_id', 'alpha_score', 'projected_pph', 'margin_sharpe', 'buy_price', 'sell_price']].head(10)
    st.table(top_df.style.format({
        'alpha_score': '{:.4f}',
        'projected_pph': '{:,.0f}',
        'margin_sharpe': '{:.2f}',
        'buy_price': '{:,.1f}',
        'sell_price': '{:,.1f}'
    }))


else:
    st.subheader("Item Analysis & History")

    item_list = df['product_id'].tolist()
    selected_item = st.selectbox("Search for an item:", item_list)

    if selected_item:
        item_data = df[df['product_id'] == selected_item].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Alpha Score", f"{item_data['alpha_score']:.4f}")
        col2.metric("Sharpe Ratio", f"{item_data['margin_sharpe']:.2f}")
        col3.metric("Proj. PPH", f"{item_data['projected_pph']:,.0f}")
        col4.metric("Hourly Vol", f"{item_data['hourly_vol']:,.0f}")

        st.write(
            f"**Current Buy:** {item_data['buy_price']:,.1f} | **Current Sell:** {item_data['sell_price']:,.1f} | **Margin (Post-Tax):** {item_data['margin']:,.1f}")

        st.write("### Last 60 Minutes Price History")
        # Fetch raw recent data for the chart
        history_df = get_recent_data(window_minutes=60)
        item_history = history_df[history_df['product_id'] == selected_item].sort_values('timestamp')

        if not item_history.empty:
            chart_data = item_history.set_index('timestamp')[['buy_price', 'sell_price']]
            st.line_chart(chart_data)
        else:
            st.warning("Not enough historical data in the DB for a chart yet.")

st.sidebar.markdown("---")
st.sidebar.write(f"Last API Sync: {pd.to_datetime('now').strftime('%H:%M:%S')}")