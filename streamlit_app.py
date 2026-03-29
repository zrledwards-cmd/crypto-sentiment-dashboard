import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import time

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CryptoSense | Market Dashboard",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS Injection ─────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

  /* Base */
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Animated gradient background */
  .stApp {
    background: linear-gradient(-45deg, #0d0d1a, #0a0f2e, #08152b, #0d0d1a);
    background-size: 400% 400%;
    animation: gradientShift 12s ease infinite;
  }
  @keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
  }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

  /* KPI card glassmorph */
  .kpi-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 24px 28px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: fadeSlideUp 0.7s ease forwards;
    opacity: 0;
  }
  .kpi-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 40px rgba(0,0,0,0.6), 0 0 30px rgba(99, 179, 237, 0.15);
  }
  @keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0px); }
  }
  .kpi-card:nth-child(1) { animation-delay: 0.1s; }
  .kpi-card:nth-child(2) { animation-delay: 0.2s; }
  .kpi-card:nth-child(3) { animation-delay: 0.3s; }
  .kpi-card:nth-child(4) { animation-delay: 0.4s; }

  .kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94a3b8 !important;
    margin-bottom: 8px;
  }
  .kpi-value {
    font-size: 2rem;
    font-weight: 900;
    color: #f1f5f9 !important;
    line-height: 1.1;
  }
  .kpi-delta-pos {
    font-size: 0.85rem;
    font-weight: 600;
    color: #34d399 !important;
    margin-top: 6px;
  }
  .kpi-delta-neg {
    font-size: 0.85rem;
    font-weight: 600;
    color: #f87171 !important;
    margin-top: 6px;
  }
  .kpi-delta-neu {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94a3b8 !important;
    margin-top: 6px;
  }

  /* Section headers */
  .section-header {
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: #93c5fd !important;
    text-transform: uppercase;
    margin: 28px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(147,197,253,0.4), transparent);
  }

  /* Hero title */
  .hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #93c5fd 0%, #c084fc 50%, #f0abfc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    animation: fadeSlideUp 0.6s ease forwards;
  }
  .hero-sub {
    font-size: 0.95rem;
    color: #64748b !important;
    margin-top: 6px;
    font-weight: 400;
    animation: fadeSlideUp 0.8s ease forwards;
  }

  /* Divider */
  .fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(147,197,253,0.3), rgba(192,132,252,0.3), transparent);
    margin: 28px 0;
    border: none;
  }

  /* Sentiment badge */
  .badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
  }
  .badge-buy  { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
  .badge-sell { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }
  .badge-hold { background: rgba(148,163,184,0.15); color: #94a3b8; border: 1px solid rgba(148,163,184,0.3); }

  /* Chart containers */
  .chart-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 8px;
    backdrop-filter: blur(10px);
  }

  /* Hide Streamlit branding */
  #MainMenu, footer { visibility: hidden; }
  [data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
COIN_META = {
    'bitcoin':  {'symbol': 'BTC', 'color': '#f59e0b', 'icon': '₿'},
    'ethereum': {'symbol': 'ETH', 'color': '#818cf8', 'icon': 'Ξ'},
    'solana':   {'symbol': 'SOL', 'color': '#34d399', 'icon': '◎'},
}
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#94a3b8', size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    hovermode='x unified',
    xaxis=dict(
        gridcolor='rgba(255,255,255,0.05)',
        showline=False,
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor='rgba(255,255,255,0.05)',
        showline=False,
        zeroline=False,
    ),
    legend=dict(
        bgcolor='rgba(0,0,0,0)',
        bordercolor='rgba(255,255,255,0.08)',
        borderwidth=1,
        orientation='h',
        yanchor='bottom', y=1.02,
        xanchor='right', x=1,
    ),
    hoverlabel=dict(
        bgcolor='rgba(15,23,42,0.95)',
        bordercolor='rgba(255,255,255,0.1)',
        font=dict(color='#f1f5f9', family='Inter'),
    ),
)

# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists('crypto_data_processed.csv'):
        return None
    df = pd.read_csv('crypto_data_processed.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
      <div style='font-size:2.5rem;'>🪙</div>
      <div style='font-size:1.1rem; font-weight:800; color:#93c5fd; letter-spacing:0.05em;'>CRYPTOSENSE</div>
      <div style='font-size:0.7rem; color:#475569; letter-spacing:0.12em; margin-top:2px;'>MARKET INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)

    df_all = load_data()
    if df_all is None:
        st.error("No data found. Run `crypto_producer.py` first.")
        st.stop()

    coins_available = sorted(df_all['coin'].unique().tolist())
    coin_labels = {c: f"{COIN_META.get(c, {}).get('icon', '')} {COIN_META.get(c, {}).get('symbol', c.upper())}" for c in coins_available}

    selected_coin = st.selectbox(
        "Asset",
        coins_available,
        format_func=lambda c: coin_labels[c],
    )
    meta = COIN_META.get(selected_coin, {'symbol': selected_coin.upper(), 'color': '#93c5fd', 'icon': '•'})

    st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.7rem; color:#475569; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:8px;'>Data Range</div>", unsafe_allow_html=True)

    coin_df_full = df_all[df_all['coin'] == selected_coin].sort_values('datetime').reset_index(drop=True)
    min_date = coin_df_full['datetime'].min().date()
    max_date = coin_df_full['datetime'].max().date()
    date_range = st.slider(
        "Select Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        label_visibility="collapsed",
    )
    st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.68rem; color:#334155; text-align:center; line-height:1.6;'>
      Data sourced from <b style='color:#475569;'>CoinGecko API</b><br>
      Indicators: RSI · SMA · Bollinger Bands<br>
      Framework: Google Data Analytics
    </div>
    """, unsafe_allow_html=True)

# ─── Main Content ─────────────────────────────────────────────────────────────
# Filter by coin and date range
coin_df = coin_df_full[
    (coin_df_full['datetime'].dt.date >= date_range[0]) &
    (coin_df_full['datetime'].dt.date <= date_range[1])
].reset_index(drop=True)

latest = coin_df.iloc[-1]
prev_24h = coin_df.iloc[-25] if len(coin_df) > 24 else coin_df.iloc[0]
prev_7d = coin_df.iloc[-(7*24)] if len(coin_df) > 7*24 else coin_df.iloc[0]

price_change_24h = ((latest['price'] - prev_24h['price']) / prev_24h['price']) * 100
price_change_7d  = ((latest['price'] - prev_7d['price'])  / prev_7d['price'])  * 100
rsi_val          = latest['rsi_14']
vol_24h          = latest['volatility_stdev_24h']

if rsi_val > 68:
    rsi_label, rsi_badge = "Overbought", "badge-sell"
elif rsi_val < 32:
    rsi_label, rsi_badge = "Oversold", "badge-buy"
else:
    rsi_label, rsi_badge = "Neutral Zone", "badge-hold"

# Hero Header
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <div class='hero-title'>{meta['icon']} {meta['symbol']} Dashboard</div>
    <div class='hero-sub'>Real-time market intelligence · Hourly data from CoinGecko · Updated as of {latest['datetime'].strftime('%b %d, %Y %H:%M')}</div>
    """, unsafe_allow_html=True)
with col_badge:
    st.markdown(f"""
    <div style='text-align:right; padding-top:18px;'>
      <span class='badge {rsi_badge}'>{rsi_label}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)

# ─── KPI Cards ────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, delta=None, delta_positive=None):
    delta_html = ""
    if delta is not None:
        if delta_positive is True:
            delta_html = f"<div class='kpi-delta-pos'>▲ {delta}</div>"
        elif delta_positive is False:
            delta_html = f"<div class='kpi-delta-neg'>▼ {delta}</div>"
        else:
            delta_html = f"<div class='kpi-delta-neu'>— {delta}</div>"
    col.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{value}</div>
      {delta_html}
    </div>
    """, unsafe_allow_html=True)

kpi(k1, "Current Price", f"${latest['price']:,.2f}",
    f"{abs(price_change_24h):.2f}% 24h", price_change_24h >= 0)
kpi(k2, "7-Day Change", f"{price_change_7d:+.2f}%",
    "vs 7 days ago", price_change_7d >= 0)
kpi(k3, "RSI (14-period)", f"{rsi_val:.1f}",
    rsi_label, None)
kpi(k4, "24h Volatility σ", f"${vol_24h:,.2f}",
    "Standard deviation", None)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ─── Chart 1: Price + Trend Analysis ─────────────────────────────────────────
st.markdown("<div class='section-header'>📈 Trend Analysis — Price & Moving Averages</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['price'],
        name='Price', mode='lines',
        line=dict(color=meta['color'], width=2.5),
        fill='tozeroy',
        fillcolor=f"rgba({int(meta['color'][1:3],16)},{int(meta['color'][3:5],16)},{int(meta['color'][5:7],16)},0.06)",
    ))
    fig_trend.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['sma_7d'],
        name='7-Day SMA', mode='lines',
        line=dict(color='#f59e0b', width=1.5, dash='dot'),
    ))
    fig_trend.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['sma_30d'],
        name='30-Day SMA', mode='lines',
        line=dict(color='#f87171', width=1.5, dash='dash'),
    ))
    layout = {**PLOTLY_LAYOUT, 'height': 400,
              'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'tickprefix': '$', 'tickformat': ',.0f'}}
    fig_trend.update_layout(**layout)
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Chart 2 & 3 side-by-side ─────────────────────────────────────────────────
col_rsi, col_vol = st.columns(2)

with col_rsi:
    st.markdown("<div class='section-header'>💡 RSI — Market Momentum</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    fig_rsi = go.Figure()
    # Shaded overbought/oversold zones
    fig_rsi.add_hrect(y0=70, y1=100, fillcolor="rgba(248,113,113,0.08)", line_width=0)
    fig_rsi.add_hrect(y0=0, y1=30, fillcolor="rgba(52,211,153,0.08)", line_width=0)
    fig_rsi.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['rsi_14'],
        name='RSI', mode='lines',
        line=dict(color='#c084fc', width=2),
    ))
    fig_rsi.add_hline(y=70, line_dash='dot', line_color='rgba(248,113,113,0.6)',
                      annotation_text='Overbought', annotation_font_color='#f87171',
                      annotation_font_size=11)
    fig_rsi.add_hline(y=30, line_dash='dot', line_color='rgba(52,211,153,0.6)',
                      annotation_text='Oversold', annotation_font_color='#34d399',
                      annotation_font_size=11)
    rsi_layout = {**PLOTLY_LAYOUT, 'height': 320,
                  'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'range': [0, 100]}}
    fig_rsi.update_layout(**rsi_layout)
    st.plotly_chart(fig_rsi, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_vol:
    st.markdown("<div class='section-header'>🌡️ Volatility — Bollinger Bands</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    fig_bb = go.Figure()
    fig_bb.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['bb_high'],
        name='Upper Band', mode='lines',
        line=dict(color='rgba(147,197,253,0.4)', width=1),
    ))
    fig_bb.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['bb_low'],
        name='Lower Band', mode='lines',
        line=dict(color='rgba(147,197,253,0.4)', width=1),
        fill='tonexty',
        fillcolor='rgba(147,197,253,0.06)',
    ))
    fig_bb.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['price'],
        name='Price', mode='lines',
        line=dict(color=meta['color'], width=2),
    ))
    bb_layout = {**PLOTLY_LAYOUT, 'height': 320,
                 'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'tickprefix': '$', 'tickformat': ',.0f'}}
    fig_bb.update_layout(**bb_layout)
    st.plotly_chart(fig_bb, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Chart 4: Volume Bar ──────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📊 Trading Volume</div>", unsafe_allow_html=True)
st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
fig_vol = go.Figure()
fig_vol.add_trace(go.Bar(
    x=coin_df['datetime'], y=coin_df['volume'],
    name='Volume',
    marker=dict(
        color=coin_df['price'].diff().apply(lambda x: '#34d399' if x >= 0 else '#f87171'),
        opacity=0.7,
    ),
))
vol_layout = {**PLOTLY_LAYOUT, 'height': 220,
              'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'tickformat': '$.2s'}}
fig_vol.update_layout(**vol_layout)
st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)

# ─── Analytics Framework Footer ───────────────────────────────────────────────
st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
with st.expander("📋 Google Data Analytics Framework: Ask → Prepare → Process → Analyze → Share"):
    c1, c2, c3, c4, c5 = st.columns(5)
    steps = [
        ("🔍", "Ask", "What signals reveal market sentiment and volatility trends across top crypto assets?"),
        ("📦", "Prepare", "90-day hourly OHLCV data fetched from the CoinGecko public API."),
        ("⚙️", "Process", "Cleaned, merged, and engineered RSI, SMA, Bollinger Bands using Python + `ta` library."),
        ("📈", "Analyze", "Identify overbought/oversold conditions, trend crossovers, and volatility clusters."),
        ("🌐", "Share", "Published as this interactive Streamlit dashboard; deployable publicly for mobile stakeholders."),
    ]
    for col, (icon, title, desc) in zip([c1,c2,c3,c4,c5], steps):
        col.markdown(f"""
        <div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:14px;
                    padding:18px 14px; text-align:center; height:100%;'>
          <div style='font-size:1.8rem;'>{icon}</div>
          <div style='font-size:0.8rem; font-weight:700; color:#93c5fd; letter-spacing:0.08em; margin:8px 0 6px;'>{title.upper()}</div>
          <div style='font-size:0.74rem; color:#64748b; line-height:1.5;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)
