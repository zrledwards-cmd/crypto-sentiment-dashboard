import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# Setup Page Configuration
st.set_page_config(page_title="Crypto Market Sentiment & Volatility", layout="wide", initial_sidebar_state="expanded")
st.title("📈 Real-Time Crypto Market Dashboard")

# Data Analytics Framework Modal
with st.expander("ℹ️ Google Data Analytics Framework: Ask, Prepare, Process, Analyze, Share"):
    st.markdown("""
    **1. Ask**: How can we monitor market trends and volatility for top cryptocurrencies in real-time?
    **2. Prepare**: Extracted 90-day hourly data from the CoinGecko API using `requests` in a Python producer.
    **3. Process**: Cleaned data and engineered Technical Indicators (RSI, Moving Averages, Bollinger Bands) using the `ta` library.
    **4. Analyze**: Identifying overbought/oversold conditions (RSI), trend reversals (SMA crossings), and volatility spikes (Bollinger widening).
    **5. Share**: This interactive Streamlit layout is optimized for both desktop and mobile viewing, fully replacing the need for Looker Studio! To deploy publicly, link this repository to Streamlit Community Cloud.
    """)

# Load Data
@st.cache_data
def load_data():
    if not os.path.exists('crypto_data_processed.csv'):
        return None
    df = pd.read_csv('crypto_data_processed.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df = load_data()

if df is None:
    st.error("No dataset found. Please run `crypto_producer.py` to fetch data.")
    st.stop()

# Sidebar Selection
coins = df['coin'].unique()
st.sidebar.header("Asset Selection")
selected_coin = st.sidebar.selectbox("Filter by Crypto Asset", coins)

# Filter Dataset for selected coin
coin_df = df[df['coin'] == selected_coin].sort_values('datetime').reset_index(drop=True)
latest_data = coin_df.iloc[-1]
# Use data from 24 hours ago for daily change
prev_day_data = coin_df.iloc[-25] if len(coin_df) > 24 else coin_df.iloc[0]

# Key Metrics Row
st.markdown("### Executive Summary")
col1, col2, col3 = st.columns(3)

with col1:
    price_change = ((latest_data['price'] - prev_day_data['price']) / prev_day_data['price']) * 100
    st.metric(
        label="Current Price (USD)", 
        value=f"${latest_data['price']:,.2f}", 
        delta=f"{price_change:.2f}% (24h)"
    )

with col2:
    rsi_val = latest_data['rsi_14']
    rsi_sentiment = "Overbought" if rsi_val > 70 else "Oversold" if rsi_val < 30 else "Neutral"
    st.metric(
        label="14-Period RSI (Sentiment)", 
        value=f"{rsi_val:.2f}",
        delta=rsi_sentiment,
        delta_color="off" if rsi_sentiment == "Neutral" else "inverse"
    )

with col3:
    st.metric(
        label="24h Volatility (Std Dev)", 
        value=f"${latest_data['volatility_stdev_24h']:.2f}"
    )

st.markdown("---")

# Chart 1: Price and Trend (SMAs)
st.markdown("#### Trend Analysis: Price vs. Moving Averages")
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=coin_df['datetime'], y=coin_df['price'], name='Price', line=dict(color='blue', width=2)))
fig_trend.add_trace(go.Scatter(x=coin_df['datetime'], y=coin_df['sma_7d'], name='7-Day SMA', line=dict(color='orange', width=2, dash='dot')))
fig_trend.add_trace(go.Scatter(x=coin_df['datetime'], y=coin_df['sma_30d'], name='30-Day SMA', line=dict(color='red', width=2, dash='dot')))
fig_trend.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), hovermode='x unified')
st.plotly_chart(fig_trend, use_container_width=True)

# Chart 2: RSI
st.markdown("#### Sentiment Momentum: Relative Strength Index (RSI)")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=coin_df['datetime'], y=coin_df['rsi_14'], name='RSI', line=dict(color='purple', width=2)))
# Overbought / Oversold Zones
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70+)")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (<30)")
fig_rsi.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(range=[0, 100]), hovermode='x unified')
st.plotly_chart(fig_rsi, use_container_width=True)

# Chart 3: Volatility (Bollinger Bands)
st.markdown("#### Volatility: Bollinger Bands")
fig_bb = go.Figure()
fig_bb.add_trace(go.Scatter(x=coin_df['datetime'], y=coin_df['bb_high'], name='Upper Band', line=dict(color='lightgray'), hoverinfo='skip'))
fig_bb.add_trace(go.Scatter(x=coin_df['datetime'], y=coin_df['bb_low'], name='Lower Band', line=dict(color='lightgray'), fill='tonexty', hoverinfo='skip'))
fig_bb.add_trace(go.Scatter(x=coin_df['datetime'], y=coin_df['price'], name='Price', line=dict(color='black', width=2)))
fig_bb.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), hovermode='x unified')
st.plotly_chart(fig_bb, use_container_width=True)

st.markdown("---")
st.markdown("*Use **Streamlit Community Cloud** (share.streamlit.io) to deploy this exact script from GitHub and receive your final public dashboard link!*")
