import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import get_session, StockPrice, StockInfo, init_db
from sqlalchemy import and_

# Initialize database on module import
init_db()

def get_nse_symbols():
    """
    Get list of NSE symbols and company names
    Returns a dictionary of symbol: company_name pairs
    """
    nse_symbols = {
        'RELIANCE.NS': 'Reliance Industries Ltd.',
        'TCS.NS': 'Tata Consultancy Services Ltd.',
        'HDFCBANK.NS': 'HDFC Bank Ltd.',
        'INFY.NS': 'Infosys Ltd.',
        'HINDUNILVR.NS': 'Hindustan Unilever Ltd.',
        'ICICIBANK.NS': 'ICICI Bank Ltd.',
        'BHARTIARTL.NS': 'Bharti Airtel Ltd.',
        'SBIN.NS': 'State Bank of India',
        'WIPRO.NS': 'Wipro Ltd.',
        'AXISBANK.NS': 'Axis Bank Ltd.',
        'ASIANPAINT.NS': 'Asian Paints Ltd.',
        'MARUTI.NS': 'Maruti Suzuki India Ltd.',
        'KOTAKBANK.NS': 'Kotak Mahindra Bank Ltd.',
        'NESTLEIND.NS': 'Nestle India Ltd.',
        'LT.NS': 'Larsen & Toubro Ltd.',
        'TATAMOTORS.NS': 'Tata Motors Ltd.',
        'BAJFINANCE.NS': 'Bajaj Finance Ltd.',
        'TITAN.NS': 'Titan Company Ltd.',
        'TECHM.NS': 'Tech Mahindra Ltd.',
        'HCLTECH.NS': 'HCL Technologies Ltd.'
    }
    return nse_symbols

def get_stock_data(symbol, period='1y'):
    """
    Fetch stock data from Yahoo Finance
    """
    try:
        # Fetch from Yahoo Finance
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist, None, None

    except Exception as e:
        return None, None, str(e)

def calculate_supertrend(df, period=10, multiplier=3):
    """Calculate Supertrend indicator"""
    hl2 = (df['High'] + df['Low']) / 2
    atr = df['High'].sub(df['Low']).rolling(window=period).mean()

    # Calculate Basic Upper and Lower Bands
    basic_ub = hl2 + (multiplier * atr)
    basic_lb = hl2 - (multiplier * atr)

    # Initialize Final Upper and Lower Bands
    final_ub = [0] * len(df)
    final_lb = [0] * len(df)
    supertrend = [0] * len(df)

    for i in range(period, len(df)):
        final_ub[i] = basic_ub[i] if (
            basic_ub[i] < final_ub[i-1] or df['Close'][i-1] > final_ub[i-1]
        ) else final_ub[i-1]

        final_lb[i] = basic_lb[i] if (
            basic_lb[i] > final_lb[i-1] or df['Close'][i-1] < final_lb[i-1]
        ) else final_lb[i-1]

        supertrend[i] = final_ub[i] if supertrend[i-1] == final_ub[i-1] and df['Close'][i] <= final_ub[i] else \
                        final_lb[i] if supertrend[i-1] == final_ub[i-1] and df['Close'][i] > final_ub[i] else \
                        final_lb[i] if supertrend[i-1] == final_lb[i-1] and df['Close'][i] >= final_lb[i] else \
                        final_ub[i] if supertrend[i-1] == final_lb[i-1] and df['Close'][i] < final_lb[i] else 0

    return pd.Series(supertrend, index=df.index)

def calculate_indicators(df):
    """Calculate basic technical indicators"""
    # 20-day Moving Average
    df['MA20'] = df['Close'].rolling(window=20).mean()

    # Relative Strength Index (14-day)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Supertrend
    df['Supertrend'] = calculate_supertrend(df)

    return df

def calculate_pivot_points(hist):
    """Calculate Pivot Points and Support/Resistance levels"""
    latest = hist.iloc[-1]
    high = latest['High']
    low = latest['Low']
    close = latest['Close']

    pivot = (high + low + close) / 3

    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)
    r4 = r3 + (high - low)

    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)
    s4 = s3 - (high - low)

    return {
        'Pivot Point': round(pivot, 2),
        'Resistance 1': round(r1, 2),
        'Resistance 2': round(r2, 2),
        'Resistance 3': round(r3, 2),
        'Resistance 4': round(r4, 2),
        'Support 1': round(s1, 2),
        'Support 2': round(s2, 2),
        'Support 3': round(s3, 2),
        'Support 4': round(s4, 2)
    }

def format_table_data(hist):
    """
    Format historical data for table display
    """
    df = hist.copy()
    df = calculate_indicators(df)
    if hasattr(df.index, 'strftime'):
        df.index = df.index.strftime('%Y-%m-%d')
    df = df.round(2)
    # Sort by date in descending order (newest first)
    df = df.sort_index(ascending=False)
    return df