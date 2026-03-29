import requests
import pandas as pd
import ta
import time

# Define parameters
COINS = ['bitcoin', 'ethereum', 'solana']
VS_CURRENCY = 'usd'
DAYS = '90'  # 90 days returns hourly data from CoinGecko

def fetch_historical_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': VS_CURRENCY,
        'days': DAYS
    }
    
    print(f"Fetching data for {coin_id}...")
    time.sleep(2)  # Respect public API rate limits
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Prices are returned as [timestamp, price]
        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])
        
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df_vol = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
        
        # Merge on timestamp
        df = pd.merge(df, df_vol, on='timestamp')
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['coin'] = coin_id
        
        return df
    except Exception as e:
        print(f"Error fetching data for {coin_id}: {e}")
        return None

def process_indicators(df):
    if df is None or df.empty:
        return df
    
    # Ensure sequential chronological order
    df = df.sort_values('datetime').reset_index(drop=True)
    
    # Technical Indicators Setup using 'ta' library
    # 1. RSI (14-period)
    df['rsi_14'] = ta.momentum.RSIIndicator(close=df['price'], window=14).rsi()
    
    # 2. Moving Averages (Hourly frequency means window needs to multiply if we want daily equivalents)
    #    7-day SMA -> 7 * 24 = 168 hours
    #    30-day SMA -> 30 * 24 = 720 hours
    df['sma_7d'] = ta.trend.SMAIndicator(close=df['price'], window=7*24).sma_indicator()
    df['sma_30d'] = ta.trend.SMAIndicator(close=df['price'], window=30*24).sma_indicator()
    
    # 3. Volatility Metrics
    # Bollinger Bands 
    indicator_bb = ta.volatility.BollingerBands(close=df['price'], window=20, window_dev=2)
    df['bb_high'] = indicator_bb.bollinger_hband()
    df['bb_low'] = indicator_bb.bollinger_lband()
    
    # Standard Deviation over last 24 hours
    df['volatility_stdev_24h'] = df['price'].rolling(window=24).std()
    
    # Round metrics for a cleaner CSV
    cols_to_round = ['price', 'volume', 'rsi_14', 'sma_7d', 'sma_30d', 'bb_high', 'bb_low', 'volatility_stdev_24h']
    df[cols_to_round] = df[cols_to_round].round(4)
    
    return df

def main():
    all_data = []
    
    for coin in COINS:
        df = fetch_historical_data(coin)
        if df is not None:
            df = process_indicators(df)
            all_data.append(df)
            
    if all_data:
        # Concatenate all coin dataframes into one
        final_df = pd.concat(all_data, ignore_index=True)
        
        # Write to Output CSV
        output_file = 'crypto_data_processed.csv'
        final_df.to_csv(output_file, index=False)
        print(f"\nSuccess! Filtered and aggregated data exported to '{output_file}'.")
        print(f"Total Rows: {len(final_df)}")
    else:
        print("\nFailed to gather data. Please check CoinGecko API status or connection.")

if __name__ == "__main__":
    main()
