import streamlit as st
import pandas as pd
import numpy as np
import requests
import ccxt
from forex_python.converter import CurrencyRates
from src.technical_analysis import display_technical_analysis
import yfinance as yf

def fetch_option_chain_nse(symbol):
    """Fetch option chain data from NSE with improved error handling"""
    try:
        # NSE option chain API
        symbol_clean = symbol.replace('.NS', '').replace('NSE:', '')
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol_clean}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/option-chain'
        }

        # First make a request to the main page to set cookies
        session = requests.Session()
        session.get('https://www.nseindia.com', headers=headers)
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if 'records' in data and 'data' in data['records']:
                # Parse the data properly
                calls_data = [item for item in data['records']['data'] if item.get('CE')]
                puts_data = [item for item in data['records']['data'] if item.get('PE')]

                if calls_data:
                    calls = pd.DataFrame([item['CE'] for item in calls_data])
                else:
                    calls = pd.DataFrame()

                if puts_data:
                    puts = pd.DataFrame([item['PE'] for item in puts_data])
                else:
                    puts = pd.DataFrame()

                return calls, puts
            else:
                st.warning("Option chain data structure changed. Using fallback method.")
                return None, None
        else:
            st.error(f"NSE API returned status code: {response.status_code}")
            return None, None
    except Exception as e:
        st.error(f"Error fetching NSE option chain: {e}")
        # Fallback to Yahoo Finance options
        try:
            st.info("Trying Yahoo Finance as fallback...")
            ticker = yf.Ticker(symbol)
            options = ticker.options
            if options:
                option_chain = ticker.option_chain(options[0])
                return option_chain.calls, option_chain.puts
        except:
            pass
        return None, None

def calculate_greeks(option_price, stock_price, strike, time_to_expiry, volatility, risk_free_rate=0.06):
    """Calculate option Greeks using Black-Scholes model"""
    try:
        from scipy.stats import norm
        import math

        d1 = (math.log(stock_price / strike) + (risk_free_rate + volatility**2 / 2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        d2 = d1 - volatility * math.sqrt(time_to_expiry)

        delta = norm.cdf(d1)
        gamma = norm.pdf(d1) / (stock_price * volatility * math.sqrt(time_to_expiry))
        theta = -stock_price * norm.pdf(d1) * volatility / (2 * math.sqrt(time_to_expiry)) - risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
        vega = stock_price * math.sqrt(time_to_expiry) * norm.pdf(d1) * 0.01
        rho = strike * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2) * 0.01

        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }
    except:
        return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}

def fetch_forex_data(pair):
    """Fetch forex data with proper error handling and multiple sources"""
    try:
        # Ensure proper forex pair format
        if not pair.endswith('=X'):
            pair = f"{pair}=X"

        data = yf.download(pair, period="1y", auto_adjust=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        st.warning(f"Yahoo Finance failed for {pair}: {e}")
        # Fallback to alternative sources
        try:
            # Try Alpha Vantage if API key is available
            import os
            api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if api_key:
                base_url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'FX_DAILY',
                    'from_symbol': pair[:3],
                    'to_symbol': pair[3:6],
                    'apikey': api_key,
                    'outputsize': 'compact'
                }
                response = requests.get(base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if 'Time Series FX (Daily)' in data:
                        df = pd.DataFrame.from_dict(data['Time Series FX (Daily)'], orient='index')
                        df = df.astype(float)
                        df.index = pd.to_datetime(df.index)
                        df = df.sort_index()
                        df.columns = ['Open', 'High', 'Low', 'Close']
                        return df
        except Exception as fallback_e:
            st.error(f"Fallback API also failed: {fallback_e}")

        return pd.DataFrame()

def fetch_crypto_data(symbol):
    """Fetch cryptocurrency data with proper formatting and multiple sources"""
    try:
        # Ensure proper crypto symbol format
        if not symbol.endswith('-USD'):
            symbol = f"{symbol}-USD"

        data = yf.download(symbol, period="1y", auto_adjust=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        st.warning(f"Yahoo Finance failed for {symbol}: {e}")
        # Fallback to CCXT for crypto data
        try:
            exchange = ccxt.binance()
            symbol_ccxt = symbol.replace('-USD', '/USDT')  # Convert to Binance format
            ohlcv = exchange.fetch_ohlcv(symbol_ccxt, timeframe='1d', limit=365)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as ccxt_e:
            st.error(f"CCXT fallback also failed: {ccxt_e}")
            return pd.DataFrame()

def analyze_forex_correlation(pairs):
    """Analyze correlation between forex pairs"""
    correlation_data = {}
    for pair in pairs:
        data = fetch_forex_data(pair)
        if not data.empty:
            correlation_data[pair] = data['Close']

    if correlation_data:
        df = pd.DataFrame(correlation_data)
        correlation_matrix = df.corr()
        return correlation_matrix
    return None

def display():
    st.header("📊 Derivatives, Forex & Crypto Analysis")

    tab1, tab2, tab3 = st.tabs(["📈 Options", "💱 Forex", "₿ Cryptocurrency"])

    with tab1:
        st.subheader("📈 Options Trading Analysis")

        symbol = st.text_input("Enter Stock Symbol for Options (e.g., NIFTY)", "NIFTY")

        if st.button("Analyze Options"):
            with st.spinner("Fetching option chain..."):
                calls, puts = fetch_option_chain_nse(symbol)

                if calls is not None and puts is not None and not calls.empty and not puts.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Call Options")
                        st.dataframe(calls[['strikePrice', 'openInterest', 'changeinOpenInterest', 'totalTradedVolume', 'impliedVolatility', 'lastPrice']].head(10))

                    with col2:
                        st.subheader("Put Options")
                        st.dataframe(puts[['strikePrice', 'openInterest', 'changeinOpenInterest', 'totalTradedVolume', 'impliedVolatility', 'lastPrice']].head(10))

                    # Greeks calculation for ATM option
                    st.subheader("Option Greeks (At-The-Money)")
                    atm_strike = calls['strikePrice'].iloc[len(calls)//2] if not calls.empty else 0
                    greeks = calculate_greeks(
                        option_price=calls['lastPrice'].iloc[len(calls)//2] if not calls.empty else 0,
                        stock_price=calls['underlyingValue'].iloc[0] if 'underlyingValue' in calls.columns else 0,
                        strike=atm_strike,
                        time_to_expiry=30/365,  # Assuming 30 days
                        volatility=0.2  # Assumed volatility
                    )
                    st.json(greeks)

                    # Recommendations
                    st.subheader("Trading Recommendations")
                    current_price = calls['underlyingValue'].iloc[0] if 'underlyingValue' in calls.columns else 0
                    atm_call = calls[calls['strikePrice'] == atm_strike]['lastPrice'].iloc[0] if not calls.empty else 0
                    atm_put = puts[puts['strikePrice'] == atm_strike]['lastPrice'].iloc[0] if not puts.empty else 0

                    if atm_call > atm_put:
                        st.success("📈 Bullish sentiment - Consider buying calls or selling puts")
                    else:
                        st.warning("📉 Bearish sentiment - Consider buying puts or selling calls")

                    # Open Interest Analysis
                    st.subheader("Open Interest Analysis")
                    max_call_oi = calls.loc[calls['openInterest'].idxmax()] if not calls.empty else None
                    max_put_oi = puts.loc[puts['openInterest'].idxmax()] if not puts.empty else None

                    if max_call_oi is not None and max_put_oi is not None:
                        st.write(f"Max Call OI at Strike: {max_call_oi['strikePrice']}")
                        st.write(f"Max Put OI at Strike: {max_put_oi['strikePrice']}")

                else:
                    st.error("Unable to fetch option chain data. Please check the symbol.")

    with tab2:
        st.subheader("💱 Forex Market Analysis")

        pairs = ["USDINR", "EURINR", "GBPINR", "JPYINR"]
        selected_pair = st.selectbox("Select Currency Pair", pairs)

        if st.button("Analyze Forex"):
            data = fetch_forex_data(selected_pair)

            if not data.empty:
                st.line_chart(data['Close'])

                # Technical indicators
                from src.technical_analysis import calculate_rsi, calculate_macd
                rsi = calculate_rsi(data)
                macd, signal = calculate_macd(data)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Price", f"₹{float(data['Close'].iloc[-1]):.2f}")
                with col2:
                    st.metric("RSI", f"{rsi.iloc[-1]:.2f}")
                with col3:
                    st.metric("MACD", f"{macd.iloc[-1]:.4f}")

                # Recommendations
                recommendation = "BUY" if rsi.iloc[-1] < 30 else "SELL" if rsi.iloc[-1] > 70 else "HOLD"
                st.metric("Recommendation", recommendation, delta=recommendation)

                # Correlation Analysis
                st.subheader("Currency Correlation")
                correlation = analyze_forex_correlation(pairs)
                if correlation is not None:
                    st.dataframe(correlation.style.background_gradient(cmap='coolwarm'))

    with tab3:
        st.subheader("₿ Cryptocurrency Analysis")

        cryptos = ["BTC-INR", "ETH-INR", "BNB-INR", "ADA-INR"]
        selected_crypto = st.selectbox("Select Cryptocurrency", cryptos)

        if st.button("Analyze Crypto"):
            data = fetch_crypto_data(selected_crypto)

            if not data.empty:
                st.line_chart(data['Close'])

                # Market metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Price", f"₹{data['Close'].iloc[-1]:.2f}")
                with col2:
                    change_pct = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100)
                    st.metric("24h Change", f"{change_pct:.2f}%", delta=f"{change_pct:.2f}%")
                with col3:
                    st.metric("Volume", f"{data['Volume'].iloc[-1]:,.0f}")
                with col4:
                    volatility = data['Close'].pct_change().std() * np.sqrt(365) * 100
                    st.metric("Volatility (Annual)", f"{volatility:.2f}%")

                # Technical analysis
                display_technical_analysis(selected_crypto)

                # Recommendations
                st.subheader("Trading Recommendations")
                rsi = calculate_rsi(data).iloc[-1]
                macd, signal = calculate_macd(data)
                macd_current = macd.iloc[-1]
                signal_current = signal.iloc[-1]

                if rsi < 30 and macd_current > signal_current:
                    st.success("🚀 Strong Buy Signal - RSI oversold and MACD bullish crossover")
                elif rsi > 70 and macd_current < signal_current:
                    st.error("📉 Strong Sell Signal - RSI overbought and MACD bearish crossover")
                elif rsi < 30:
                    st.info("💪 Buy Signal - RSI indicates oversold conditions")
                elif rsi > 70:
                    st.warning("⚠️ Sell Signal - RSI indicates overbought conditions")
                else:
                    st.info("⏳ Hold - Wait for clearer signals")
