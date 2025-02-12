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

    .title {
        font-family: 'Arial Black', sans-serif;
        font-size: 2.5em;
        font-weight: bold;
        color: #1E3D59;
        text-align: center;
        margin-bottom: 20px;
    }

    .price-display {
        font-size: 1.8em;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        margin: 10px 0;
    }

    .level-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        height: 100%;  /* Make all boxes same height */
        display: flex;
        flex-direction: column;
    }

    .level-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .turning-price {
        color: orange;
        font-weight: bold;
        font-size: 28px;
        text-align: center;
        margin: 15px 0;
    }

    .level-item {
        padding: 5px 0;
        text-align: center;
        font-size: 16px;
        margin: 2px 0;
    }

    .level-title {
        text-align: center;
        margin-bottom: 10px;
        font-size: 1.2em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Title with Angel One logo
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="title">📊 NSE Stock Data Analysis</div>', unsafe_allow_html=True)
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
        # Get current price
        current_price = hist.iloc[-1]['Close']

        # Display current price and symbol
        st.markdown(f"""
        <div class="price-display">
            {symbol.replace('.NS', '')} - Current Price: ₹{current_price:.2f}
        </div>
        """, unsafe_allow_html=True)

        # Calculate and display pivot points
        pivot_points = calculate_pivot_points(hist)
        st.markdown("<h3 style='margin-bottom: 20px; text-align: center;'>Support and Resistance levels for Intraday Trading</h3>", unsafe_allow_html=True)

        # Display resistance levels in ascending order
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="level-box">', unsafe_allow_html=True)
            st.markdown('<div class="level-title">Support Levels</div>', unsafe_allow_html=True)
            st.markdown('<div class="level-content">', unsafe_allow_html=True)
            for i in range(1, 5):
                st.markdown(f'<div class="level-item" style="color: red;">S{i}: ₹{pivot_points[f"Support {i}"]}</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="level-box">', unsafe_allow_html=True)
            st.markdown('<div class="level-title">Turning Price</div>', unsafe_allow_html=True)
            st.markdown('<div class="level-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="turning-price">₹{pivot_points["Pivot Point"]}</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="level-box">', unsafe_allow_html=True)
            st.markdown('<div class="level-title">Resistance Levels</div>', unsafe_allow_html=True)
            st.markdown('<div class="level-content">', unsafe_allow_html=True)
            for i in range(1, 5):
                st.markdown(f'<div class="level-item" style="color: green;">R{i}: ₹{pivot_points[f"Resistance {i}"]}</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

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

        # Add Supertrend
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Supertrend'],
            mode='lines',
            name='Supertrend',
            line=dict(color='purple', width=2)
        ))

        # Improve chart layout
        fig.update_layout(
            title=f"{symbol.replace('.NS', '')} Stock Price",
            yaxis_title="Price (₹)",
            xaxis_title="Date",
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=600,  # Increase chart height
            margin=dict(t=30, r=30, b=30, l=30),  # Add margins
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255, 255, 255, 0.1)"
            ),
            # Improve date axis formatting
            xaxis=dict(
                rangeslider=dict(visible=False),
                type="date",
                tickformat="%Y-%m-%d",
                tickmode="auto",
                nticks=20,  # Adjust number of date labels
                tickangle=-45,  # Angle the date labels
                showgrid=True,
                gridcolor="rgba(255, 255, 255, 0.1)"
            ),
            # Improve price axis formatting
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(255, 255, 255, 0.1)",
                zeroline=False
            ),
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
            paper_bgcolor="rgba(0,0,0,0)"
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