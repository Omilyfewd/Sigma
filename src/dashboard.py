import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis import merged_data, filtering
from data_eda import get_recent_data

st.set_page_config(page_title="Lawrence is a Skibidi Sigma", layout="wide")
st.title("📈 Lawrence Shi Quantitative Trading and Market Analysis Tool")

@st.cache_data(ttl=60)
def load_processed_data():
    raw_merged = merged_data(window_hours=12)
    return filtering(raw_merged, cap=5)

df = load_processed_data() #lag spike on load data

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Market Leaderboard 🔥", "Item \'Drill-down\' Details 🐱"])

if page == "Market Leaderboard 🔥":
    st.subheader("Top Risk-Adjusted Flips (Using my Alpha Score)")
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

        st.write("### Swag Price History chart (Last 60m) using Plotly")

        history_df = get_recent_data(window_minutes=60)
        item_history = history_df[history_df['product_id'] == selected_item].copy()

        if not item_history.empty:
            item_history['timestamp'] = pd.to_datetime(item_history['timestamp'], unit='ms')
            item_history = item_history.sort_values('timestamp')

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=item_history['timestamp'],
                y=item_history['buy_price'],
                mode='lines+markers',
                name='Buy Price',
                line=dict(color='#00ff00') #green
            ))

            fig.add_trace(go.Scatter(
                x=item_history['timestamp'],
                y=item_history['sell_price'],
                mode='lines',
                name='Sell Price',
                line=dict(color='#ff0000', dash='dash') #red
            ))

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Time",
                yaxis_title="Coins",
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough data yet...")

st.sidebar.markdown("---")
st.sidebar.write(f"Last API Sync: {pd.to_datetime('now').strftime('%H:%M:%S')}")

# Credit: https://www.kdnuggets.com/how-to-combine-streamlit-pandas-and-plotly-for-interactive-data-apps