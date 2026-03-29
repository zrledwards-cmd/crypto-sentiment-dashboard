# Real-Time Crypto Market Dashboard

An interactive, real-time dashboard built with **Python**, **Streamlit**, and the **CoinGecko API** to monitor cryptocurrency market sentiment, trends, and volatility.

## Overview
This project applies the **Google Data Analytics Framework** (Ask, Prepare, Process, Analyze, Share) to the cryptocurrency markets:
- **Ask**: How do we precisely track real-time trends and momentum for top assets like Bitcoin, Ethereum, and Solana?
- **Prepare**: We securely pull 90-day hourly historical data directly from the CoinGecko public API without requiring API keys.
- **Process**: Data is cleaned, sequenced, and merged utilizing `pandas`.
- **Analyze**: We compute critical technical indicators using the `ta` library:
  - **RSI (14-period)** for overbought/oversold momentum.
  - **SMA (7-day & 30-day)** to identify macro bullish/bearish trends.
  - **Bollinger Bands & 24h Std Dev** to visualize tightening or expanding market volatility.
- **Share**: The final deliverable is an aesthetically pleasing, responsive **Streamlit** dashboard deployable for mobile stakeholders.

## Installation & Local Usage

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd crypto_dashboard
```

### 2. Set up the virtual environment
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate 

pip install -r requirements.txt
```

### 3. Fetch the latest market data
Run the producer script to call the CoinGecko API, compute the latest indicators, and update the dataset in real-time.
```bash
python crypto_producer.py
```

### 4. Run the Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```
Open `http://localhost:8501` in your browser to view the interactive application!

## Deployment
To deploy this project so anyone can access it on their mobile phone via a public link:
1. Ensure this directory is a GitHub repository.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click "New App", connect your GitHub account, and select the `crypto_dashboard` repository.
4. Set the main file path to `streamlit_app.py` and hit **Deploy**!
