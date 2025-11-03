import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from src.data_fetcher import fetch_historical_data

def calculate_rsi(data, period=14):
    """Calculate RSI"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data):
    """Calculate MACD"""
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def plot_technical_chart(data, symbol):
    """Plot interactive technical chart"""
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(x=data.index,
                open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close']))

    # Moving Averages
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(50).mean(), name='50 MA'))
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(200).mean(), name='200 MA'))

    # RSI
    rsi = calculate_rsi(data)
    fig.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI', yaxis='y2'))

    fig.update_layout(
        title=f'{symbol} Technical Analysis',
        yaxis_title='Price',
        yaxis2=dict(title='RSI', overlaying='y', side='right'),
        xaxis_rangeslider_visible=False
    )

    return fig

def generate_recommendation(data):
    """Generate buy/sell recommendations based on technical indicators"""
    rsi = calculate_rsi(data).iloc[-1]
    macd, signal = calculate_macd(data)
    macd_current = macd.iloc[-1]
    signal_current = signal.iloc[-1]

    if rsi < 30 and macd_current > signal_current:
        return "BUY"
    elif rsi > 70 and macd_current < signal_current:
        return "SELL"
    else:
        return "HOLD"

def display_technical_analysis(symbol):
    data = fetch_historical_data(symbol)

    st.subheader("Technical Analysis")

    # Interactive Chart
    fig = plot_technical_chart(data, symbol)
    st.plotly_chart(fig)

    # Indicators
    col1, col2, col3 = st.columns(3)
    with col1:
        rsi = calculate_rsi(data).iloc[-1]
        st.metric("RSI", f"{rsi:.2f}")
    with col2:
        macd, signal = calculate_macd(data)
        st.metric("MACD", f"{macd.iloc[-1]:.2f}")
    with col3:
        recommendation = generate_recommendation(data)
        st.metric("Recommendation", recommendation)
