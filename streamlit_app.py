import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CryptoSense | Market Dashboard",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Animated gradient background — deep teal-to-charcoal */
  .stApp {
    background: linear-gradient(-45deg, #0b0f0f, #0d1a18, #091515, #0b1010);
    background-size: 400% 400%;
    animation: gradientShift 14s ease infinite;
  }
  @keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
  }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

  /* Hero */
  .hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #fbbf24 0%, #fb923c 45%, #f43f5e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    animation: fadeUp 0.6s ease forwards;
  }
  .hero-sub {
    font-size: 0.9rem;
    color: #6b7280 !important;
    margin-top: 6px;
    animation: fadeUp 0.8s ease forwards;
  }
  @keyframes fadeUp {
    from { opacity:0; transform:translateY(20px); }
    to   { opacity:1; transform:translateY(0); }
  }

  /* Coin nav bar */
  .coin-nav {
    display: flex;
    gap: 12px;
    margin: 18px 0 4px;
    flex-wrap: wrap;
  }
  .coin-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 22px;
    border-radius: 50px;
    border: 1.5px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(10px);
    cursor: pointer;
    font-size: 0.88rem;
    font-weight: 700;
    color: #94a3b8;
    transition: all 0.25s ease;
    letter-spacing: 0.04em;
    text-shadow: none;
  }
  .coin-btn:hover {
    border-color: rgba(251,191,36,0.5);
    background: rgba(251,191,36,0.08);
    color: #fbbf24;
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(251,191,36,0.15);
  }
  .coin-btn-btc.active {
    border-color: #f59e0b;
    background: rgba(245,158,11,0.15);
    color: #fbbf24;
    box-shadow: 0 0 20px rgba(245,158,11,0.3);
  }
  .coin-btn-eth.active {
    border-color: #a78bfa;
    background: rgba(167,139,250,0.15);
    color: #c4b5fd;
    box-shadow: 0 0 20px rgba(167,139,250,0.3);
  }
  .coin-btn-sol.active {
    border-color: #2dd4bf;
    background: rgba(45,212,191,0.15);
    color: #5eead4;
    box-shadow: 0 0 20px rgba(45,212,191,0.3);
  }

  /* KPI cards */
  .kpi-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    padding: 22px 24px;
    backdrop-filter: blur(20px);
    box-shadow: 0 6px 28px rgba(0,0,0,0.35);
    transition: transform 0.3s, box-shadow 0.3s;
    animation: fadeUp 0.7s ease both;
  }
  .kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 14px 38px rgba(0,0,0,0.5), 0 0 24px rgba(251,146,60,0.1);
  }
  .kpi-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #6b7280 !important;
    margin-bottom: 8px;
  }
  .kpi-value {
    font-size: 1.9rem;
    font-weight: 900;
    color: #f9fafb !important;
    line-height: 1.1;
  }
  .kpi-delta-pos { font-size:0.82rem; font-weight:600; color:#34d399 !important; margin-top:5px; }
  .kpi-delta-neg { font-size:0.82rem; font-weight:600; color:#f87171 !important; margin-top:5px; }
  .kpi-delta-neu { font-size:0.82rem; font-weight:600; color:#6b7280 !important; margin-top:5px; }

  /* Section headers — coral/amber tones */
  .section-header {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #fb923c !important;
    text-transform: uppercase;
    margin: 26px 0 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(251,146,60,0.35), transparent);
  }

  /* Divider */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(251,146,60,0.25), rgba(244,63,94,0.2), transparent);
    margin: 24px 0;
    border: none;
  }

  /* Badge */
  .badge { display:inline-block; padding:4px 12px; border-radius:999px; font-size:0.73rem; font-weight:700; letter-spacing:0.07em; }
  .badge-buy  { background:rgba(52,211,153,0.12); color:#34d399; border:1px solid rgba(52,211,153,0.3); }
  .badge-sell { background:rgba(248,113,113,0.12); color:#f87171; border:1px solid rgba(248,113,113,0.3); }
  .badge-hold { background:rgba(107,114,128,0.15); color:#9ca3af; border:1px solid rgba(107,114,128,0.3); }

  /* Chart box */
  .chart-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 6px;
  }

  /* Streamlit tab overrides */
  [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
  }
  [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    color: #6b7280 !important;
    padding: 8px 20px !important;
    letter-spacing: 0.05em !important;
  }
  [aria-selected="true"] {
    background: rgba(251,146,60,0.18) !important;
    color: #fb923c !important;
  }

  /* Hide defaults */
  #MainMenu, footer { visibility: hidden; }
  [data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
COIN_META = {
    'bitcoin':  {'symbol': 'BTC', 'name': 'Bitcoin',  'color': '#f59e0b', 'icon': '₿', 'btn_class': 'coin-btn-btc'},
    'ethereum': {'symbol': 'ETH', 'name': 'Ethereum', 'color': '#a78bfa', 'icon': 'Ξ', 'btn_class': 'coin-btn-eth'},
    'solana':   {'symbol': 'SOL', 'name': 'Solana',   'color': '#2dd4bf', 'icon': '◎', 'btn_class': 'coin-btn-sol'},
}
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#6b7280', size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    hovermode='x unified',
    xaxis=dict(gridcolor='rgba(255,255,255,0.04)', showline=False, zeroline=False),
    yaxis=dict(gridcolor='rgba(255,255,255,0.04)', showline=False, zeroline=False),
    legend=dict(
        bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.07)', borderwidth=1,
        orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
    ),
    hoverlabel=dict(
        bgcolor='rgba(10,15,15,0.96)', bordercolor='rgba(255,255,255,0.08)',
        font=dict(color='#f9fafb', family='Inter'),
    ),
)

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists('crypto_data_processed.csv'):
        return None
    df = pd.read_csv('crypto_data_processed.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df_all = load_data()
if df_all is None:
    st.error("No dataset found. Please run `crypto_producer.py` first.")
    st.stop()

coins_available = sorted(df_all['coin'].unique().tolist())

# ─── Brand Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero-title'>🪙 CryptoSense</div>
<div class='hero-sub'>Real-time market intelligence · RSI · Moving Averages · Volatility · Hourly data via CoinGecko</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─── Coin Selection Tabs (prominent top menu) ─────────────────────────────────
st.markdown("<div class='section-header'>SELECT ASSET</div>", unsafe_allow_html=True)

tab_labels = []
for c in coins_available:
    m = COIN_META.get(c, {'icon': '•', 'symbol': c.upper()})
    tab_labels.append(f"{m['icon']} {m['symbol']}")

tabs = st.tabs(tab_labels)

# ─── Per-Coin Views ───────────────────────────────────────────────────────────
def kpi(col, label, value, delta=None, pos=None, delay="0s"):
    delta_html = ""
    if delta:
        cls = "kpi-delta-pos" if pos is True else "kpi-delta-neg" if pos is False else "kpi-delta-neu"
        arrow = "▲" if pos is True else "▼" if pos is False else "—"
        delta_html = f"<div class='{cls}'>{arrow} {delta}</div>"
    col.markdown(f"""
    <div class='kpi-card' style='animation-delay:{delay}'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{value}</div>
      {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_coin_tab(coin):
    meta = COIN_META.get(coin, {'symbol': coin.upper(), 'color': '#fb923c', 'icon': '•'})
    color = meta['color']
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    coin_df_full = df_all[df_all['coin'] == coin].sort_values('datetime').reset_index(drop=True)

    # Date range slider
    min_d = coin_df_full['datetime'].min().date()
    max_d = coin_df_full['datetime'].max().date()
    d1, d2 = st.select_slider(
        "Date Range",
        options=sorted(coin_df_full['datetime'].dt.date.unique()),
        value=(min_d, max_d),
        label_visibility="collapsed",
        key=f"date_range_{coin}",
    )
    coin_df = coin_df_full[
        (coin_df_full['datetime'].dt.date >= d1) &
        (coin_df_full['datetime'].dt.date <= d2)
    ].reset_index(drop=True)

    latest   = coin_df.iloc[-1]
    prev_24h = coin_df.iloc[-25] if len(coin_df) > 24 else coin_df.iloc[0]
    prev_7d  = coin_df.iloc[-(7*24)] if len(coin_df) > 7*24 else coin_df.iloc[0]

    chg_24h = ((latest['price'] - prev_24h['price']) / prev_24h['price']) * 100
    chg_7d  = ((latest['price'] - prev_7d['price'])  / prev_7d['price'])  * 100
    rsi_val = latest['rsi_14']
    vol_24h = latest['volatility_stdev_24h']

    if rsi_val > 68:   rsi_label, rsi_badge = "Overbought", "badge-sell"
    elif rsi_val < 32: rsi_label, rsi_badge = "Oversold",   "badge-buy"
    else:              rsi_label, rsi_badge = "Neutral",     "badge-hold"

    # Sub-header
    col_h, col_b = st.columns([4, 1])
    with col_h:
        st.markdown(f"""
        <div style='font-size:1.6rem; font-weight:900; color:{color}; margin:14px 0 2px;'>
          {meta['icon']} {meta['name']} <span style='color:#374151; font-size:1rem;'>({meta['symbol']})</span>
        </div>
        <div style='font-size:0.82rem; color:#4b5563;'>
          Updated {latest['datetime'].strftime('%b %d, %Y %H:%M UTC')}
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<div style='text-align:right; padding-top:22px;'><span class='badge {rsi_badge}'>{rsi_label}</span></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Current Price", f"${latest['price']:,.2f}",  f"{abs(chg_24h):.2f}% · 24h",  chg_24h >= 0,  "0.1s")
    kpi(k2, "7-Day Change",  f"{chg_7d:+.2f}%",           "vs 7 days ago",                chg_7d  >= 0,  "0.2s")
    kpi(k3, "RSI 14-Period", f"{rsi_val:.1f}",             rsi_label,                      None,          "0.3s")
    kpi(k4, "24h Volatility σ", f"${vol_24h:,.2f}",        "Std deviation",                None,          "0.4s")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Chart 1: Trend ──────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>📈 Price & Moving Averages</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['price'], name='Price', mode='lines',
        line=dict(color=color, width=2.5),
        fill='tozeroy', fillcolor=f'rgba({r},{g},{b},0.07)',
    ))
    fig_t.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['sma_7d'], name='7d SMA', mode='lines',
        line=dict(color='#fbbf24', width=1.5, dash='dot'),
    ))
    fig_t.add_trace(go.Scatter(
        x=coin_df['datetime'], y=coin_df['sma_30d'], name='30d SMA', mode='lines',
        line=dict(color='#f43f5e', width=1.5, dash='dash'),
    ))
    fig_t.update_layout(**{**PLOTLY_LAYOUT, 'height': 400,
                           'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'tickprefix': '$', 'tickformat': ',.0f'}})
    st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Chart 2 & 3 side-by-side ────────────────────────────────────────────
    c_rsi, c_bb = st.columns(2)

    with c_rsi:
        st.markdown("<div class='section-header'>💡 RSI — Momentum</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        fig_rsi = go.Figure()
        fig_rsi.add_hrect(y0=70, y1=100, fillcolor="rgba(248,113,113,0.07)", line_width=0)
        fig_rsi.add_hrect(y0=0,  y1=30,  fillcolor="rgba(52,211,153,0.07)",  line_width=0)
        fig_rsi.add_trace(go.Scatter(
            x=coin_df['datetime'], y=coin_df['rsi_14'], name='RSI', mode='lines',
            line=dict(color='#fb923c', width=2),
        ))
        fig_rsi.add_hline(y=70, line_dash='dot', line_color='rgba(248,113,113,0.5)',
                          annotation_text='Overbought', annotation_font_color='#f87171', annotation_font_size=11)
        fig_rsi.add_hline(y=30, line_dash='dot', line_color='rgba(52,211,153,0.5)',
                          annotation_text='Oversold', annotation_font_color='#34d399', annotation_font_size=11)
        fig_rsi.update_layout(**{**PLOTLY_LAYOUT, 'height': 310,
                                 'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'range': [0, 100]}})
        st.plotly_chart(fig_rsi, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c_bb:
        st.markdown("<div class='section-header'>🌡️ Bollinger Bands</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        fig_bb = go.Figure()
        fig_bb.add_trace(go.Scatter(
            x=coin_df['datetime'], y=coin_df['bb_high'], name='Upper', mode='lines',
            line=dict(color=f'rgba({r},{g},{b},0.35)', width=1),
        ))
        fig_bb.add_trace(go.Scatter(
            x=coin_df['datetime'], y=coin_df['bb_low'], name='Lower', mode='lines',
            line=dict(color=f'rgba({r},{g},{b},0.35)', width=1),
            fill='tonexty', fillcolor=f'rgba({r},{g},{b},0.05)',
        ))
        fig_bb.add_trace(go.Scatter(
            x=coin_df['datetime'], y=coin_df['price'], name='Price', mode='lines',
            line=dict(color=color, width=2),
        ))
        fig_bb.update_layout(**{**PLOTLY_LAYOUT, 'height': 310,
                                'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'tickprefix': '$', 'tickformat': ',.0f'}})
        st.plotly_chart(fig_bb, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Chart 4: Volume ──────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Trading Volume</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    fig_v = go.Figure()
    fig_v.add_trace(go.Bar(
        x=coin_df['datetime'], y=coin_df['volume'], name='Volume',
        marker=dict(
            color=coin_df['price'].diff().apply(lambda x: '#34d399' if x >= 0 else '#f87171'),
            opacity=0.65,
        ),
    ))
    fig_v.update_layout(**{**PLOTLY_LAYOUT, 'height': 210,
                           'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'tickformat': '$.2s'}})
    st.plotly_chart(fig_v, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Framework footer ─────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    with st.expander("📋 Google Data Analytics Framework"):
        fc = st.columns(5)
        steps = [
            ("🔍", "Ask",     "What signals reveal market sentiment and volatility trends?"),
            ("📦", "Prepare", "90-day hourly OHLCV data from CoinGecko public API."),
            ("⚙️", "Process", "Cleaned data; RSI, SMA & Bollinger Bands via `ta` + `pandas`."),
            ("📈", "Analyze", "Identify crossovers, overbought zones, and volatility spikes."),
            ("🌐", "Share",   "Deployed as a public Streamlit dashboard, mobile-friendly."),
        ]
        for col, (icon, title, desc) in zip(fc, steps):
            col.markdown(f"""
            <div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
                        border-radius:14px; padding:16px 12px; text-align:center;'>
              <div style='font-size:1.6rem;'>{icon}</div>
              <div style='font-size:0.75rem; font-weight:700; color:#fb923c; letter-spacing:0.08em; margin:8px 0 5px;'>{title.upper()}</div>
              <div style='font-size:0.72rem; color:#4b5563; line-height:1.5;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── Render each tab ──────────────────────────────────────────────────────────
for tab, coin in zip(tabs, coins_available):
    with tab:
        render_coin_tab(coin)
