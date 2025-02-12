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
        info = stock.info
        return hist, info, None
    except Exception as e:
        return None, None, str(e)

def get_tradingview_symbol(symbol):
    """Convert Yahoo Finance symbol to TradingView format"""
    return f"NSE:{symbol.replace('.NS', '')}"

def calculate_indicators(df):
    """Calculate technical indicators"""
    # 20-day Moving Average
    df['MA20'] = df['Close'].rolling(window=20).mean()

    # Relative Strength Index (14-day)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Supertrend (10,3)
    period = 10
    multiplier = 3

    # Calculate True Range
    df['tr0'] = abs(df['High'] - df['Low'])
    df['tr1'] = abs(df['High'] - df['Close'].shift(1))
    df['tr2'] = abs(df['Low'] - df['Close'].shift(1))
    df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
    df['atr'] = df['tr'].rolling(period).mean()

    # Calculate basic bands
    hl2 = (df['High'] + df['Low']) / 2

    # Basic Upper and Lower Bands
    df['basic_ub'] = hl2 + (multiplier * df['atr'])
    df['basic_lb'] = hl2 - (multiplier * df['atr'])

    # Final Upper and Lower Bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or df['Close'].iat[i - 1] > df['final_ub'].iat[i - 1] else df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or df['Close'].iat[i - 1] < df['final_lb'].iat[i - 1] else df['final_lb'].iat[i - 1]

    # Supertrend
    df['supertrend'] = 0.00
    for i in range(period, len(df)):
        if df['Close'].iat[i] <= df['final_ub'].iat[i]:
            df['supertrend'].iat[i] = df['final_ub'].iat[i]
        else:
            df['supertrend'].iat[i] = df['final_lb'].iat[i]

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