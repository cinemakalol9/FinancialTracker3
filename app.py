import streamlit as st
import pandas as pd
from utils import get_stock_data, format_table_data, calculate_pivot_points

# Page configuration
st.set_page_config(
    page_title="NSE Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit branding
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Custom CSS for clean look
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    div.stDataFrame {
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .stTextInput > div > div {
        background-color: white;
        border-radius: 5px;
    }

    .stSelectbox > div > div {
        background-color: white;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Title with Angel One logo
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 NSE Stock Data")
with col2:
    st.image("assets/app-icon.svg", width=200)

st.markdown("Enter a stock symbol (without .NS) and select time period to view historical data")

# Add Angel One signup link
st.markdown("""
<div style='text-align: center; margin-top: 10px;'>
    <h4>Account Open In Angel One - <a href='https://www.angelone.in/signup/register?rne_source=B2B_NXT&btype=SVRQUg&referrer=PRL%3A%3Arne_source%3DB2B_NXT%3A%3Abtype%3DSVRQUg&source_caller=api&pid=NXT&sbtag=UFJM&is_retargeting=false&shortlink=3nknzmxn&deep_link_value=referrer%3DPRL%3A%3Arne_source%3DB2B_NXT%3A%3Abtype%3DSVRQUg&c=nxt_campaign' target='_blank'>Click Here</a></h4>
</div>
""", unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([2, 1])
with col1:
    raw_symbol = st.text_input("Stock Symbol (e.g., RELIANCE, TCS, INFY)", "").upper()
    # Add .NS suffix if not present
    symbol = f"{raw_symbol}.NS" if raw_symbol and not raw_symbol.endswith('.NS') else raw_symbol

with col2:
    period = st.selectbox(
        "Time Period",
        options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
        index=3
    )

if symbol:
    # Add a loading spinner
    with st.spinner(f'Fetching data for {symbol}...'):
        hist, _, error = get_stock_data(symbol, period)

    if error:
        st.error(f"Error fetching data: {error}")
    elif hist is not None:
        # Calculate and display pivot points
        pivot_points = calculate_pivot_points(hist)
        st.markdown("<h3 style='margin-bottom: 20px;'>Below Support and Resistance levels Just for Intraday</h3>", unsafe_allow_html=True)
        
        # Display resistance levels in ascending order
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Support Levels")
            for i in range(1, 5):
                st.markdown(f"<span style='color: red'>S{i}: ₹{pivot_points[f'Support {i}']}</span>", unsafe_allow_html=True)
                
        with col2:
            st.markdown("### Turning Price")
            st.markdown(f"<span style='color: orange; font-weight: bold; font-size: 24px'>₹{pivot_points['Pivot Point']}</span>", unsafe_allow_html=True)
            
        with col3:
            st.markdown("### Resistance Levels")
            for i in range(1, 5):
                st.markdown(f"<span style='color: green'>R{i}: ₹{pivot_points[f'Resistance {i}']}</span>", unsafe_allow_html=True)

        # Candlestick chart
        st.subheader("Price Chart (Candlestick)")
        import plotly.graph_objects as go
        
        # Create dataframe for charts
        df = format_table_data(hist)
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        )])
        
        fig.update_layout(
            title=f"{symbol.replace('.NS', '')} Stock Price",
            yaxis_title="Price (₹)",
            xaxis_title="Date",
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Enhanced Volume Chart
        st.subheader("Trading Volume")
        fig_volume = go.Figure()
        
        # Color volume bars based on price movement
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(df['Close'], df['Open'])]
        
        fig_volume.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors
        ))
        
        # Add 20-day moving average of volume
        fig_volume.add_trace(go.Scatter(
            x=df.index,
            y=df['Volume'].rolling(window=20).mean(),
            name='20-day MA',
            line=dict(color='orange', width=2)
        ))
        
        fig_volume.update_layout(
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Volume",
            showlegend=True
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)

        # Historical data table
        st.subheader(f"Historical Data - {symbol.replace('.NS', '')}")
        df = format_table_data(hist)
        st.dataframe(df, use_container_width=True)

        # Download button
        csv = df.to_csv()
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"{symbol.replace('.NS', '')}_stock_data.csv",
            mime="text/csv"
        )
    else:
        st.error("No data found for the given symbol")
else:
    st.info("👆 Enter a stock symbol above to get started!")
