import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List
import csv
import io
import ta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import time

# Page config
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# Define country markets and their major indices
COUNTRY_INDICES = {
    "USA": "^GSPC",  # S&P 500
    "India": "^BSESN",  # BSE SENSEX
    "Japan": "^N225",  # Nikkei 225
    "UK": "^FTSE",  # FTSE 100
    "Germany": "^GDAXI",  # DAX
    "China": "000001.SS",  # Shanghai Composite
    "Hong Kong": "^HSI",  # Hang Seng
    "Canada": "^GSPTSE",  # S&P/TSX Composite
    "Australia": "^AXJO",  # ASX 200
    "Singapore": "^STI"  # Straits Times Index
}

#Currency Symbols
CURRENCY_SYMBOLS = {
    "USA": "$",
    "India": "₹",
    "Japan": "¥",
    "UK": "£",
    "Germany": "€",
    "China": "¥",
    "Hong Kong": "HK$",
    "Canada": "C$",
    "Australia": "A$",
    "Singapore": "S$"
}

# Define sectors and major companies for each country
MARKET_SECTORS: Dict[str, Dict[str, List[str]]] = {
    "USA": {
        "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "META"],
        "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK"],
        "Financial": ["JPM", "BAC", "WFC", "GS", "MS"],
        "Consumer": ["AMZN", "WMT", "PG", "KO", "PEP"],
        "Industrial": ["BA", "CAT", "GE", "MMM", "HON"]
    },
    "India": {
        "Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS", "LTI.NS"],
        "Financial": ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
        "Consumer": ["ITC.NS", "HINDUNILVR.NS", "BRITANNIA.NS", "DABUR.NS", "MARICO.NS"],
        "Industrial": ["LT.NS", "ADANIENT.NS", "SIEMENS.NS", "ABB.NS", "HAVELLS.NS"],
        "Healthcare": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "BIOCON.NS"]
    },
   "Japan": {
        "Technology": ["SONY", "TOSYY", "NTDOY", "7731.T", "4755.T"],
        "Financial": ["8306.T", "8411.T", "8316.T", "8604.T", "8766.T"],
        "Consumer": ["7203.T", "7267.T", "7269.T", "6954.T", "6752.T"],
        "Industrial": ["7011.T", "7012.T", "6301.T", "6305.T", "7751.T"],
        "Healthcare": ["4502.T", "4519.T", "4568.T", "4543.T", "4523.T"]
    },
    "UK": {
        "Technology": ["ARM.L", "SAGE.L", "AUTO.L", "SOPH.L", "AVV.L"],
        "Financial": ["HSBA.L", "BARC.L", "LLOY.L", "STAN.L", "NWG.L"],
        "Consumer": ["ULVR.L", "DGE.L", "BATS.L", "TSCO.L", "RB.L"],
        "Industrial": ["RR.L", "BA.L", "BNZL.L", "EXPN.L", "CRH.L"],
        "Healthcare": ["GSK.L", "AZN.L", "SHL.L", "HIK.L", "BTG.L"]
    },
    "Germany": {
        "Technology": ["SAP.DE", "IFX.DE", "DTE.DE", "SOW.DE", "OSR.DE"],
        "Financial": ["DBK.DE", "CBK.DE", "ALV.DE", "MUV2.DE", "WDI.DE"],
        "Consumer": ["BAS.DE", "BAYN.DE", "BEI.DE", "HEN3.DE", "FME.DE"],
        "Industrial": ["SIE.DE", "LHA.DE", "RWE.DE", "VOW3.DE", "DAI.DE"],
        "Healthcare": ["FRE.DE", "MRK.DE", "BAYN.DE", "PAH3.DE", "SHL.DE"]
    },
    "China": {
        "Technology": ["600519.SS", "000063.SZ", "600703.SS", "002230.SZ", "600460.SS"],
        "Financial": ["601398.SS", "601939.SS", "601288.SS", "601988.SS", "600036.SS"],
        "Consumer": ["600887.SS", "600660.SS", "601633.SS", "601888.SS", "601933.SS"],
        "Industrial": ["601618.SS", "601669.SS", "601390.SS", "601766.SS", "601800.SS"],
        "Healthcare": ["600276.SS", "600867.SS", "002007.SZ", "600518.SS", "600196.SS"]
    },
    "Hong Kong": {
        "Technology": ["0700.HK", "2382.HK", "9988.HK", "3690.HK", "2318.HK"],
        "Financial": ["0005.HK", "0939.HK", "1398.HK", "3988.HK", "2318.HK"],
        "Consumer": ["0001.HK", "0016.HK", "0027.HK", "0175.HK", "0267.HK"],
        "Industrial": ["0388.HK", "0003.HK", "0066.HK", "0083.HK", "0836.HK"],
        "Healthcare": ["1093.HK", "1177.HK", "2318.HK", "2383.HK", "3320.HK"]
    },
    "Canada": {
        "Technology": ["SHOP.TO", "CSU.TO", "OTEX.TO", "BB.TO", "LSPD.TO"],
        "Financial": ["RY.TO", "TD.TO", "BNS.TO", "BMO.TO", "CM.TO"],
        "Consumer": ["L.TO", "ATD.TO", "EMP.TO", "MRU.TO", "WN.TO"],
        "Industrial": ["CN.TO", "CP.TO", "CAE.TO", "WSP.TO", "STN.TO"],
        "Healthcare": ["SIA.TO", "GUD.TO", "CXR.TO", "CRH.TO", "DR.TO"]
    },
    "Australia": {
        "Technology": ["XRO.AX", "APT.AX", "WTC.AX", "CPU.AX", "TNE.AX"],
        "Financial": ["CBA.AX", "WBC.AX", "ANZ.AX", "NAB.AX", "MQG.AX"],
        "Consumer": ["WES.AX", "WOW.AX", "COL.AX", "TCL.AX", "SGP.AX"],
        "Industrial": ["BHP.AX", "RIO.AX", "FMG.AX", "NCM.AX", "ORI.AX"],
        "Healthcare": ["CSL.AX", "RMD.AX", "SHL.AX", "COH.AX", "ANN.AX"]
    },
    "Singapore": {
        "Technology": ["A17U.SI", "C38U.SI", "J69U.SI", "M44U.SI", "ME8U.SI"],
        "Financial": ["D05.SI", "O39.SI", "U11.SI", "Z74.SI", "BN4.SI"],
        "Consumer": ["C07.SI", "C31.SI", "F34.SI", "J36.SI", "N21.SI"],
        "Industrial": ["U96.SI", "S68.SI", "S63.SI", "V03.SI", "Y92.SI"],
        "Healthcare": ["BSL.SI", "C52.SI", "M01.SI", "RF7U.SI", "Z74.SI"]
    }
}

SECTOR_ETFS = {
    "Technology": "XLK",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Consumer Discretionary": "XLY",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Consumer Staples": "XLP",
    "Utilities": "XLU",
    "Communication Services": "XLC"
}


# CSS with theme-dependent styles
st.markdown("""
    <style>
    @keyframes writing {
        from { width: 0; }
        to { width: 100%; }
    }
    .magic-text {
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        border-right: 2px solid #FFD700;
        padding-right: 5px;
        animation: writing 2s steps(40, end);
        background: linear-gradient(45deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 20px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .insight-box {
        background-color: #1e1e1e;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .insight-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar layout
st.sidebar.markdown("""<div style='text-align: center'>
    <span class='magic-text'>Stock Market Dashboard ✨</span></div>""", 
    unsafe_allow_html=True)

st.sidebar.header("Market Selection")

# Country selection
selected_country = st.sidebar.selectbox(
    "Select Country",
    options=list(COUNTRY_INDICES.keys()),
    index=1  # Default = India
)

# Sector selection (only show sectors for selected country)
available_sectors = list(MARKET_SECTORS.get(selected_country, {}).keys())
selected_sectors = st.sidebar.multiselect(
    "Select Sectors",
    options=available_sectors,
    default=[]
)

# Stock selection based on selected sectors
available_stocks = []
if selected_sectors:
    for sector in selected_sectors:
        available_stocks.extend(MARKET_SECTORS[selected_country][sector])
    
    stocks = st.sidebar.multiselect(
        "Select Stocks",
        options=available_stocks,
        default=[]
    )
else:
    stocks = []

# Time frame selection
time_frame = st.sidebar.selectbox(
    "Select Time Frame",
    ('Daily', 'Weekly', 'Monthly')
)

# Chart type selection
chart_type = st.sidebar.radio(
    "Select Chart Type",
    ('Line Chart', 'Area Chart', 'Bar Chart')
)



def generate_market_insights(sector_data):
    """Generate market insights based on sector performance"""
    insights = []
    
    if sector_data and 'Rank A: Real-Time Performance' in sector_data:
        # Sort sectors by performance
        performances = []
        for sector, performance in sector_data['Rank A: Real-Time Performance'].items():
            perf_value = float(performance.strip('%'))
            performances.append((sector, perf_value))
        
        # Sort by performance value
        performances.sort(key=lambda x: x[1], reverse=True)
        
        # Generate insights for top performing sectors
        for sector, perf_value in performances:
            triangle = "▲" if perf_value >= 0 else "▼"
            color = "green" if perf_value >= 0 else "red"
            
            insight = f"""
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <span style='color: {color}; font-size: 20px; margin-right: 10px;'>{triangle}</span>
                <span>{sector} sector is showing 
                <span style='color: {color};'>{perf_value:.2f}%</span> performance</span>
            </div>
            """
            insights.append(insight)
        
        # Add summary insights
        top_sector = performances[0][0]
        bottom_sector = performances[-1][0]
        
        summary = f"""
        <div style='margin-top: 15px; padding: 10px; border-top: 1px solid #444;'>
            <p><strong>Key Insights:</strong></p>
            <p>• {top_sector} is leading the market</p>
            <p>• {bottom_sector} is showing the weakest performance</p>
        </div>
        """
        insights.append(summary)
    
    return insights

# Update the CSS styles
st.markdown("""
    <style>
    .insight-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .insight-box {
        background-color: #1e1e1e;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

#Sector Data
def get_sector_data_yf(country: str):
    """Fetch sector data using yfinance for the selected country"""
    sector_data = {}
    if country in MARKET_SECTORS:
        for sector, stocks in MARKET_SECTORS[country].items():
            try:
                # Calculate average performance of sector stocks
                performances = []
                for stock in stocks:
                    data = yf.download(stock, period="1mo", progress=False)
                    if not data.empty:
                        start_price = data['Close'].iloc[0]
                        end_price = data['Close'].iloc[-1]
                        performance = ((end_price - start_price) / start_price) * 100
                        performances.append(performance)
                
                if performances:
                    avg_performance = sum(performances) / len(performances)
                    sector_data[sector] = f"{avg_performance:.2f}%"
                
            except Exception as e:
                print(f"Error fetching data for {sector}: {str(e)}")
                sector_data[sector] = "0.00%"
    
    if sector_data:
        return {'Rank A: Real-Time Performance': sector_data}
    return None

def plot_technical_analysis(data, stock):
    # Create subplot
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5,0.1,0.2,0.2])

    # Convert Close price to series if it's not already
    close_data = pd.Series(data['Close'].values.flatten(), index=data.index)
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=close_data,
        name='Price'
    ))

    # Add Moving averages
    fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], name='50 Day MA', line=dict(color='orange', width=1)))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], name='200 Day MA', line=dict(color='green', width=1)))

    # Volume
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'), row=2, col=1)

    # RSI
    try:
        rsi = ta.momentum.RSIIndicator(close_data).rsi()
        fig.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI'), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    except Exception as e:
        st.warning(f"Unable to calculate RSI: {str(e)}")

    # MACD
    try:
        macd = ta.trend.MACD(close_data)
        fig.add_trace(go.Scatter(x=data.index, y=macd.macd(), name='MACD'), row=4, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=macd.macd_signal(), name='Signal'), row=4, col=1)
        fig.add_bar(x=data.index, y=macd.macd_diff(), name='MACD Histogram', row=4, col=1)
    except Exception as e:
        st.warning(f"Unable to calculate MACD: {str(e)}")

    # Update layout
    fig.update_layout(
        title=f'{stock} Technical Analysis',
        xaxis_rangeslider_visible=False,
        height=900,
        width=800,
        showlegend=True
    )
    
    st.plotly_chart(fig)

def plot_volume_analysis(data, stock):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Ensure data is 1D
    close_data = data['Close'].squeeze()
    open_data = data['Open'].squeeze()

    # Price chart
    fig.add_trace(go.Scatter(x=data.index, y=close_data, name='Close Price', line=dict(color='blue', width=1)), row=1, col=1)

    # Volume chart
    colors = ['green' if close > open else 'red' for close, open in zip(close_data, open_data)]
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color=colors), row=2, col=1)

    # Add Moving Average Volume
    ma_vol = data['Volume'].rolling(window=20).mean()
    fig.add_trace(go.Scatter(x=data.index, y=ma_vol, name='20 Day MA Volume', line=dict(color='orange', width=1)), row=2, col=1)

    # Update layout
    fig.update_layout(title=f'{stock} Volume Analysis', height=600, width=800)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    st.plotly_chart(fig)


def plot_technical_analysis(data, stock):
    # Create subplot
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5,0.1,0.2,0.2])

    # Ensure data is properly formatted as 1D series
    close_data = data['Close'].values.flatten() if isinstance(data['Close'], pd.DataFrame) else data['Close']
    close_series = pd.Series(close_data, index=data.index)

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=close_series,
        name='Price'
    ))

    # Add Moving averages
    fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], name='50 Day MA', line=dict(color='orange', width=1)))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], name='200 Day MA', line=dict(color='green', width=1)))

    # Volume
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'), row=2, col=1)

    # RSI
    try:
        rsi = ta.momentum.RSIIndicator(close_series).rsi()
        fig.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI'), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    except Exception as e:
        st.warning(f"Unable to calculate RSI: {str(e)}")

    # MACD
    try:
        macd = ta.trend.MACD(close_series)
        fig.add_trace(go.Scatter(x=data.index, y=macd.macd(), name='MACD'), row=4, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=macd.macd_signal(), name='Signal'), row=4, col=1)
        fig.add_bar(x=data.index, y=macd.macd_diff(), name='MACD Histogram', row=4, col=1)
    except Exception as e:
        st.warning(f"Unable to calculate MACD: {str(e)}")

    # Update layout
    fig.update_layout(
        title=f'{stock} Technical Analysis',
        xaxis_rangeslider_visible=False,
        height=900,
        width=800,
        showlegend=True
    )
    
    st.plotly_chart(fig)

def fetch_stock_data(tickers):
    data = {}
    with st.spinner('Fetching stock data... '):
        for ticker in tickers:
            try:
                df = yf.download(ticker, period='1y')
                if not df.empty:
                    df['MA50'] = df['Close'].rolling(window=50).mean()
                    df['MA200'] = df['Close'].rolling(window=200).mean()
                    data[ticker] = df
                else:
                    st.warning(f"No data available for {ticker}")
            except Exception as e:
                st.error(f"Error fetching data for {ticker}: {str(e)}")
    return data


def stream_market_analysis(selected_country):
    yield f"## Market Analysis - {selected_country}\n \n"
    time.sleep(0.5)

    #Fetch sector data
    sector_data = get_sector_data_yf(selected_country)

    if sector_data:
        yield "Analyzing sector performance..... \n\n"
        time.sleep(1.5)

        #Generate insights
        insights = generate_market_insights(sector_data)
        for insight in insights:
            for sentence in insight.split("\n"):
                yield sentence + "\n"
                time.sleep(0.4)
    else:
        yield "Unable to fetch sector data. Please try again..."

        time.sleep(0.8)
    #About
    yield "\n About This Dashboard \n \n"

    time.sleep(1.5)

    about_text = """
    Welcome to your personal window into the dynamic world of stock markets!

    This dashboard is designed to be your go-to companion for navigating the complex landscape of financial markets.
      
    Whether you're a seasoned investor or just starting out.

    • Real-time market insights tailored to your selected country

    • Comprehensive stock analysis with interactive graphs

    • Side-by-side stock comparisons to inform your investment decisions

    • Technical indicators to gauge market sentiment

    But that's not all! We believe in empowering you with knowledge. 

    That's why we've included a dedicated Data section 
    
    Where you can dive deep into the raw numbers behind our analysis.
     
    It's all about transparency see the data we use, understand our process, and make informed decisions with confidence.

    So, are you ready to embark on your financial journey? 
    
    Select your stocks, explore the insights, and let's make some informed investment decisions together!

    """
    
    for paragraph in about_text.split('\n'):
        if paragraph.strip():
            yield paragraph + "\n"
            time.sleep(0.4)    
    
def resample_data(data, time_frame):
    if data is not None and not data.empty:
        if time_frame == 'Daily':
            return data
        elif time_frame == 'Weekly':
            return data.resample('W').last()
        elif time_frame == 'Monthly':
            return data.resample('M').last()
    return None


def generate_market_insights(sector_data):
    """Generate market insights based on sector performance"""
    insights = []
    
    if sector_data and 'Rank A: Real-Time Performance' in sector_data:
        # Sort sectors by performance
        performances = []
        for sector, performance in sector_data['Rank A: Real-Time Performance'].items():
            perf_value = float(performance.strip('%'))
            performances.append((sector, perf_value))
        
        # Sort by performance value
        performances.sort(key=lambda x: x[1], reverse=True)
        
        # Only add summary insights
        top_sector = performances[0][0]
        bottom_sector = performances[-1][0]
        
        summary = f"""
        Key Insights:
        • {top_sector} is leading the market
        • {bottom_sector} is showing the weakest performace
        """
        insights.append(summary)
    
    return insights

def plot_stock_data(stock_data, time_frame, tickers, chart_type):
    valid_data_count = 0
    # BG Color
    is_dark_theme = st.get_option("theme.base") == 'dark'
    background_color = "#0E1117" if is_dark_theme else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark_theme else "#0E1117"
    figs = []  # Store figures to avoid duplicates

    for ticker in tickers:
        filtered_data = resample_data(stock_data[ticker], time_frame)
        if filtered_data is not None and not filtered_data.empty:
            valid_data_count += 1
            
            # Add title for each stock before its graph
            st.markdown(f"### {ticker} Stock Analysis", help=f"Analyzing {ticker} stock data")
            
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor(background_color)
            ax.set_facecolor(background_color)
            # Set colors for all text elements
            ax.tick_params(colors=text_color)
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            ax.title.set_color(text_color)

            # Your existing plotting code...
            adj_close = filtered_data['Adj Close'].squeeze()

            if chart_type == 'Line Chart':
                ax.plot(filtered_data.index, adj_close, label="Adj Close")
                ax.plot(filtered_data.index, filtered_data['MA50'], label="50 Day MA")
                ax.plot(filtered_data.index, filtered_data['MA200'], label='200 Day MA')
            elif chart_type == 'Area Chart':
                ax.fill_between(filtered_data.index, adj_close, where=adj_close.notna(), label="Adj Close", alpha=0.5)
                ax.plot(filtered_data.index, filtered_data['MA50'], label="50 Day MA")
                ax.plot(filtered_data.index, filtered_data['MA200'], label="200 Day MA")
            elif chart_type == "Bar Chart":
                daily_returns = adj_close.pct_change().fillna(0)
                colors = ['green' if float(x) >= 0 else 'red' for x in daily_returns]
                ax.bar(filtered_data.index, daily_returns, label="Daily Returns", alpha=0.7, color=colors)
                ax.axhline(y=0, color=text_color, linestyle='--', linewidth=0.5)

            ax.set_title(f"{ticker} Stock Prices ({time_frame})", color=text_color)
            ax.set_xlabel("Date", color=text_color)
            ax.set_ylabel("Price", color=text_color)
            legend = ax.legend(bbox_to_anchor=(1, 0), loc="lower left")
            plt.setp(legend.get_texts(), color=text_color)
            
            for spine in ax.spines.values():
                spine.set_color(text_color)
            
            fig.autofmt_xdate()
            st.pyplot(fig)  # Plot each figure immediately after creating it
            
            # Add a separator between stocks
            if ticker != tickers[-1]:  # Don't add separator after the last stock
                st.markdown("---")
        else:
            st.write(f"No data available for {ticker} at the {time_frame} time frame.")

    if valid_data_count == 0:
        st.write("No valid data available for the selected stocks and time frame.")

def generate_pdf(stock_data, time_frame, stocks, chart_type):
    """Generate PDF report for stock analysis"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, height - 40, "Stock Market Analysis Report")
    
    # Add date
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 60, f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Add parameters
    c.drawString(30, height - 80, f"Time Frame: {time_frame}")
    c.drawString(30, height - 100, f"Chart Type: {chart_type}")
    
    # Add stocks analyzed
    c.drawString(30, height - 120, "Stocks Analyzed:")
    y_position = height - 140
    for stock in stocks:
        c.drawString(50, y_position, f"• {stock}")
        y_position -= 20
    
    # Add summary statistics
    y_position -= 20
    c.drawString(30, y_position, "Summary Statistics:")
    for stock in stocks:
        if stock in stock_data and not stock_data[stock].empty:
            data = stock_data[stock]
            # Convert Series to float values
            current_price = float(data['Close'].iloc[-1])
            start_price = float(data['Close'].iloc[0])
            change = ((current_price - start_price) / start_price) * 100
            
            y_position -= 20
            c.drawString(50, y_position, 
                f"• {stock}: Current Price: ${current_price:.2f}, Change: {change:.2f}%")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def generate_csv(stock_data):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Stock', 'Date', 'Close'])
    for stock, data in stock_data.items():
        for date, row in data.iterrows():
            writer.writerow([stock, date, row['Close']])
    return output.getvalue()

def calculate_investment_score(stock_data):
    """Calculate investment score based on multiple technical indicators"""

    try:
        close_prices = stock_data['Close'].squeeze()

        #Get existing calculations
        rsi = ta.momentum.RSIIndicator(close_prices).rsi().iloc[-1]
        macd = ta.trend.MACD(close_prices)
        macd_diff = macd.macd_diff().iloc[-1]

        #Taking the existing data from the code
        short_ma = stock_data['MA50'].iloc[-1]
        long_ma = stock_data['MA200'].iloc[-1]
        current_price = close_prices.iloc[-1]

        #calculate volatility
        volatility = float(stock_data['Close'].pct_change().std() * np.sqrt(252) *100)

        #Scoring System
        score = 0

        #RSI Analysis
        if rsi < 30: score +=2 #Oversold
        elif rsi < 40: score +=1
        elif rsi > 70: score -=2 #Overbrought
        elif rsi > 60: score -= 1

        #MACD Analysis
        if macd_diff > 0: score +=1
        else: score -= 1

        #Moving Average Analysis
        if current_price > short_ma: score +=1
        if current_price > long_ma: score +=1
        if short_ma > long_ma: score +=1

        #Voltility Analysis
        if volatility < 20: score += 1 #Less than 20% volatility
        if volatility > 40: score -=1 #More than 40% volatility

        return score, {
            'RSI': rsi,
            'MACD': macd_diff,
            'Volatility': volatility,
            'Price vs 50MA': (current_price - short_ma) / short_ma *100,
            'Price vs 200MA': (current_price - long_ma) / long_ma * 100
        }
    except Exception as e:
        st.error(f"Error calculating investment score: {str(e)}")
        return None, None
    
def get_investment_recommendation(score):
    """Convert numercial score to recommendation"""
    if score >=4:
        return "Strong Buy", "Success"
    elif score >= 2:
        return "Buy", "info"
    elif score >= 0:
        return "Hold", "Warning"
    elif score >= -2:
        return "Sell", "Error"
    else:
        return "Strong sell", "Error"

#Simplified Performance Tracker
if 'performance_tracker' not in st.session_state:
    st.session_state.performance_tracker = {}

        
#Main Code

if not stocks:  # When no stocks are selected, show sector analysis
  st.write_stream(stream_market_analysis(selected_country))
  st.write("Remember, the market waits for no one let's get started!")

if stocks:  # If stocks are selected
    if time_frame:
        with st.spinner('Fetching stock data...'):
            stock_data = fetch_stock_data(stocks)
            
            # Create two columns for title and download button
            col1, col2 = st.columns([3, 1])
            
            # Add titles and information in the left column
            with col1:
                if len(stocks) == 1:
                    st.title(f"Analysis for {stocks[0]}")
                else:
                    st.title("Analysis for Selected Stocks:")
                    stock_list = ", ".join(stocks)
                    st.markdown(f"**Selected Stocks:** {stock_list}")
                
                # Add time frame and chart type information
                st.markdown(f"**Time Frame:** {time_frame} | **Chart Type:** {chart_type}")
            
            # Add download preparation in the right column
            with col2:
                st.write("")  # Add some spacing
                st.write("")  # Add more spacing to align with title
                if st.button("Generate Report"):
                    with st.spinner("Generating report..."):
                        # Generate PDF report
                        pdf = generate_pdf(stock_data, time_frame, stocks, chart_type)
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf,
                            file_name="stock_analysis_report.pdf",
                            mime="application/pdf"
                        )
                        
                        # Generate CSV data
                        csv = generate_csv(stock_data)
                        st.download_button(
                            label="Download CSV Data",
                            data=csv,
                            file_name="stock_data.csv",
                            mime="text/csv"
                        )

            # Add a separator
            st.markdown("---")
            
            # Create tabs
            summary_tab, graph_tab, comparison_tab, data_tab = st.tabs([
                "📊 Summary", 
                "📈 Graph", 
                "🔄 Comparison",
                "🗃 Data"
            ])

           # 1. Summary Tab
            with summary_tab:
                # First Section: Stock Analysis Summary
                st.subheader("Stock Analysis Summary")
                
                # Create columns for all stocks
                cols = st.columns(3)
                col_index = 0
                
                for stock in stocks:
                    if stock in stock_data and not stock_data[stock].empty:
                        data = stock_data[stock]
                        
                        try:
                            # Ensure Close price is 1D series
                            close_series = data['Close'] if isinstance(data['Close'], pd.Series) else data['Close'].squeeze()
                            
                            # Calculate RSI
                            rsi = ta.momentum.RSIIndicator(close_series).rsi()
                            last_rsi = rsi.iloc[-1]
                            
                            # Display metrics in columns
                            with cols[col_index % 3]:
                                st.write(f"### {stock}")
                                current_price = float(close_series.iloc[-1])
                                currency_symbol = CURRENCY_SYMBOLS[selected_country]
                                st.metric("Current Price", f"{currency_symbol}{current_price:.2f}")
                                
                                start_price = float(close_series.iloc[0])
                                change = ((current_price - start_price) / start_price) * 100
                                st.metric("Overall Change", f"{change:.2f}%")
                                
                                st.metric("RSI", f"{last_rsi:.2f}")
                                st.markdown("---")
                            
                            col_index += 1
                            
                        except Exception as e:
                            st.warning(f"Unable to calculate metrics for {stock}: {str(e)}")
                
                # Second Section: Investment Analysis
                st.header("Investment Analysis")
                
                st.warning("""
                ⚠️ **Investment Analysis Disclaimer:**
                - The recommendations provided are based on technical analysis only
                - Past performance does not guarantee future results
                - This is not professional financial advice
                - Always conduct your own research and consult with a financial advisor before making investment decisions
                """)
                
                # Create columns for investment analysis
                analysis_cols = st.columns(2)
                analysis_col_index = 0
                
                for stock in stocks:
                    if stock in stock_data and not stock_data[stock].empty:
                        score, metrics = calculate_investment_score(stock_data[stock])
                        
                        if score is not None and metrics is not None:
                            recommendation, status = get_investment_recommendation(score)
                            
                            with analysis_cols[analysis_col_index % 2]:
                                st.subheader(f"{stock} Analysis")
                                
                                # Display recommendation
                                st.metric(
                                    label="Recommendation",
                                    value=recommendation,
                                    delta=f"Score: {score}"
                                )
                                
                                # Display key metrics in a more compact format
                                metrics_cols = st.columns(2)
                                metric_items = list(metrics.items())
                                
                                for i, (metric_name, value) in enumerate(metric_items):
                                    with metrics_cols[i % 2]:
                                        st.metric(
                                            label=metric_name,
                                            value=f"{value:.2f}"
                                        )
                                
                                # Add detailed analysis in expander
                                with st.expander(f"Detailed Analysis"):
                                    st.write("### Technical Indicators Analysis")
                                    
                                    # RSI Analysis
                                    st.write("**RSI Analysis**")
                                    if metrics['RSI'] < 30:
                                        st.write("- RSI indicates oversold condition (Bullish)")
                                    elif metrics['RSI'] > 70:
                                        st.write("- RSI indicates overbought conditions (Bearish)")
                                    else:
                                        st.write("- RSI indicates neutral conditions")
                                    
                                    # MACD Analysis
                                    st.write("**MACD Analysis:**")
                                    if metrics['MACD'] > 0:
                                        st.write("- MACD shows bullish momentum")
                                    else:
                                        st.write("- MACD shows bearish momentum")
                                    
                                    # Moving Averages Analysis
                                    st.write("**Moving Averages Analysis**")
                                    if metrics['Price vs 50MA'] > 0:
                                        st.write(f"- Price is {metrics['Price vs 50MA']:.2f}% above 50-day MA (Bullish)")
                                    else:
                                        st.write(f"- Price is {abs(metrics['Price vs 50MA']):.2f}% below 50-day MA (Bearish)")
                                    
                                    # Volatility Analysis
                                    st.write("**Volatility Analysis**")
                                    if metrics['Volatility'] < 20:
                                        st.write("- Low volatility: stable conditions")
                                    elif metrics['Volatility'] > 40:
                                        st.write("- High volatility: risky conditions")
                                    else:
                                        st.write("- Moderate volatility conditions")
                                
                                st.markdown("---")
                                analysis_col_index += 1


            # 2. Graph Tab
            with graph_tab:
                st.subheader("Technical Analysis")
                
                # Add chart type selector in the graph tab
                chart_options = st.radio(
                    "Select Chart View",
                    ['Standard', 'Advanced Technical', 'Volume Analysis'],
                    horizontal=True
                )
                
                if chart_options == 'Standard':
                    plot_stock_data(stock_data, time_frame, stocks, chart_type)
                elif chart_options == 'Advanced Technical':
                    for stock in stocks:
                        if stock in stock_data and not stock_data[stock].empty:
                            plot_technical_analysis(stock_data[stock], stock)
                else:  # Volume Analysis
                    for stock in stocks:
                        if stock in stock_data and not stock_data[stock].empty:
                            plot_volume_analysis(stock_data[stock], stock)

            # 3. Comparison Tab
            with comparison_tab:
                st.subheader("Stock Comparison Analysis")
                if len(stocks) == 1:
                    st.write("Need more than one stock for comparison!")
                elif len(stocks) > 1:
                    # Initialize DataFrame with columns
                    comparison_df = pd.DataFrame(columns=[
                        'Return (%)', 'Volatility (%)', 
                        'Risk-Adjusted Return', 'Sentiment Score'
                    ])

                    # Keep track of processed stocks
                    processed_stocks = set()
                    
                    # Compare selected stocks
                    for stock in stocks:
                        if stock not in processed_stocks and stock in stock_data:
                            processed_stocks.add(stock)

                            if not stock_data[stock].empty:
                                try:
                                    data = stock_data[stock]
                                    
                                    # Calculate metrics
                                    returns = float(((data['Close'].iloc[-1] - data['Close'].iloc[0]) / 
                                            data['Close'].iloc[0]) * 100)
                                    volatility = float(data['Close'].pct_change().std() * 
                                                np.sqrt(252) * 100)
                                    risk_adj_return = float(returns / volatility if volatility > 0 else 0)
                                
                                    # Simulate sentiment analysis
                                    sentiment_score = np.random.uniform(-1, 1)

                                    # Add to DataFrame
                                    comparison_df.loc[stock] = {
                                        'Return (%)': returns,
                                        'Volatility (%)': volatility,
                                        'Risk-Adjusted Return': risk_adj_return,
                                        'Sentiment Score': sentiment_score
                                    }
                                except Exception as e:
                                    st.warning(f"Error calculating metrics for {stock}: {str(e)}")
                    
                    if not comparison_df.empty:
                        st.dataframe(comparison_df.style.format({
                            'Return (%)': '{:.2f}%',
                            'Volatility (%)': '{:.2f}%',
                            'Risk-Adjusted Return': '{:.2f}',
                            'Sentiment Score': '{:.2f}'
                        }))
                    else:
                        st.warning("No valid comparison data available")
                    
                    st.header("Performance Changes")
                    for stock in stocks:
                        if stock in stock_data and not stock_data[stock].empty:
                            current_price = stock_data[stock]['Close'].iloc[-1]

                            # Ensure current_price is float
                            if isinstance(current_price, pd.Series):
                                current_price = current_price.iloc[0]
                            current_price = float(current_price)
                            
                            # Initialize or update tracker
                            if stock not in st.session_state.performance_tracker:
                                st.session_state.performance_tracker[stock] = {
                                    'initial_price': current_price,
                                    'last_check': time.strftime('%Y-%m-%d')
                                }
                            
                            # Calculate changes
                            initial_change = ((current_price - st.session_state.performance_tracker[stock]['initial_price']) / 
                                            st.session_state.performance_tracker[stock]['initial_price'] * 100)

                            # Display Metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                currency_symbol = CURRENCY_SYMBOLS.get(selected_country, '$')
                                st.metric(
                                    label=f"{stock}",
                                    value=f"{currency_symbol}{current_price:.2f}",
                                    delta=f"{initial_change:.2f}% since {st.session_state.performance_tracker[stock]['last_check']}"
                                )
                                
            # 4. Data Tab
            with data_tab:
                st.subheader("Raw Data")
                for stock in stocks:
                    if stock in stock_data and not stock_data[stock].empty:
                        st.write(f"### {stock} Data")
                        
                        try:
                            # Convert index to datetime if it's not already
                            data = stock_data[stock].copy()
                            data.index = pd.to_datetime(data.index)
                            
                            # Get min and max dates
                            min_date = data.index.min().date()
                            max_date = data.index.max().date()
                            
                            # Add a date range selector
                            date_range = st.date_input(
                                f"Select date range for {stock}",
                                value=(min_date, max_date),
                                min_value=min_date,
                                max_value=max_date,
                                key=f"date_range_{stock}"
                            )
                            
                            if len(date_range) == 2:
                                start_date, end_date = date_range
                                mask = (data.index.date >= start_date) & (data.index.date <= end_date)
                                filtered_data = data[mask]
                                
                                if not filtered_data.empty:
                                    st.dataframe(filtered_data)
                                    
                                    # Add download button for the filtered data
                                    csv = filtered_data.to_csv()
                                    st.download_button(
                                        label=f"Download {stock} Data",
                                        data=csv,
                                        file_name=f"{stock}_data.csv",
                                        mime="text/csv"
                                    )
                                else:
                                    st.warning("No data available for the selected date range.")
                            
                        except Exception as e:
                            st.error(f"Error processing data for {stock}: {str(e)}")
                            