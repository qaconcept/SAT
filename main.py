import streamlit as st
import yfinance as yf
import json
import os
import time
from functools import wraps

# Config
SAVE_FILE = "fed_settings.json"
MAX_RETRIES = 3
RETRY_DELAY = 1

# Initialize session state for analysis results
if 'analyzed_stocks' not in st.session_state:
    st.session_state.analyzed_stocks = []


# ---- Error Handling Decorator ----
def retry_yfinance(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            st.error(f"Failed to fetch data after {max_retries} attempts. Error: {str(last_error)}")
            return None

        return wrapper

    return decorator

# ---- Data Fetching with Retries ----
@st.cache_data
@retry_yfinance()
def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            raise ValueError(f"No data found for {ticker}")
        return {
            "revenue_growth": info.get("revenueGrowth", 0) * 100,
            "earnings_growth": info.get("earningsGrowth", 0) * 100,
            "pe_ratio": info.get("trailingPE", 0),
            "debt_ebitda": info.get("debtToEbitda", 0),
        }
    except Exception as e:
        raise RuntimeError(f"Yahoo Finance error for {ticker}: {str(e)}")

# ---- Save/Load Fed Settings ----
def save_fed_settings(settings):
    with open(SAVE_FILE, "w") as f:
        json.dump(settings, f)


def load_fed_settings():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {"rates": "high", "balance_sheet": "decreasing"}


# ---- Stock Evaluation Logic ----
def evaluate_stock(fed_rates, fed_balance_sheet, revenue_growth, earnings_growth, pe_ratio, debt_ebitda):
    score = 0
    if fed_rates == "high" and fed_balance_sheet == "decreasing":
        if pe_ratio <= 15 and debt_ebitda <= 2:
            score += 2
        elif revenue_growth >= 5 and earnings_growth >= 5:
            score += 1
    elif fed_rates == "low" and fed_balance_sheet == "increasing":
        if revenue_growth > 50 and pe_ratio > 25:
            score += 2
        elif revenue_growth >= 20 and earnings_growth >= 10:
            score += 1
    if earnings_growth < 0:
        score -= 1
    if debt_ebitda > 5:
        score -= 2
    elif debt_ebitda <= 1:
        score += 1
    return "Strong Buy (0-50%)" if score >= 3 else "Moderate Buy (0-20%)" if score >= 1 else "Avoid (0%)"


# ---- Streamlit UI ----
st.title("📈 Stock Investment Analyzer")
st.markdown("""
**Features**:  
- Analyze 3 stocks with real-time data  
- Save/Load Fed policy preferences  
- Auto-retry on API failures  
""")

# Load saved Fed settings
fed_settings = load_fed_settings()

# 1. Federal Reserve Inputs
st.header("1. Federal Reserve Policy")
col1, col2 = st.columns(2)
with col1:
    fed_rates = st.selectbox("Interest Rates", ["high", "low"], index=0 if fed_settings["rates"] == "high" else 1)
with col2:
    fed_balance_sheet = st.selectbox("Balance Sheet Trend", ["increasing", "decreasing"],
                                     index=0 if fed_settings["balance_sheet"] == "increasing" else 1)

if st.button("💾 Save Fed Settings"):
    save_fed_settings({"rates": fed_rates, "balance_sheet": fed_balance_sheet})
    st.success("Settings saved!")

# 2. Stock Inputs (3 stocks)
st.header("2. Stock Metrics")
use_auto_fetch = st.toggle("Auto-Fetch Data (Yahoo Finance)", True, help="Disable to enter metrics manually")

# Clear results if Fed settings change
if 'last_fed_settings' not in st.session_state:
    st.session_state.last_fed_settings = (fed_rates, fed_balance_sheet)
else:
    if (fed_rates, fed_balance_sheet) != st.session_state.last_fed_settings:
        st.session_state.analyzed_stocks = []
        st.session_state.last_fed_settings = (fed_rates, fed_balance_sheet)

# Track which stocks have been analyzed
analyzed_indices = set()

for i in range(3):
    st.subheader(f"Stock {i + 1}")
    ticker = st.text_input(f"Ticker {i + 1}", key=f"ticker_{i}", placeholder="AAPL").strip().upper()

    if use_auto_fetch and ticker:
        with st.spinner(f"Fetching data for {ticker}..."):
            data = fetch_stock_data(ticker)

        if data:
            revenue_growth = st.number_input(f"Revenue Growth (%) {i + 1}", value=data["revenue_growth"],
                                             key=f"rev_{i}")
            earnings_growth = st.number_input(f"Earnings Growth (%) {i + 1}", value=data["earnings_growth"],
                                              key=f"earn_{i}")
            pe_ratio = st.number_input(f"P/E Ratio {i + 1}", value=data["pe_ratio"], key=f"pe_{i}")
            debt_ebitda = st.number_input(f"Debt/EBITDA {i + 1}", value=data["debt_ebitda"], key=f"debt_{i}")
        else:
            st.error(f"⚠️ Could not fetch data for {ticker}. Please check the ticker or enter metrics manually.")
            continue
    else:
        revenue_growth = st.number_input(f"Revenue Growth (%) {i + 1}", key=f"rev_{i}")
        earnings_growth = st.number_input(f"Earnings Growth (%) {i + 1}", key=f"earn_{i}")
        pe_ratio = st.number_input(f"P/E Ratio {i + 1}", key=f"pe_{i}")
        debt_ebitda = st.number_input(f"Debt/EBITDA {i + 1}", key=f"debt_{i}")

    # Analyze button for each stock
    if st.button(f"Analyze Stock {i + 1}", key=f"btn_{i}"):
        if ticker:
            recommendation = evaluate_stock(
                fed_rates, fed_balance_sheet, revenue_growth,
                earnings_growth, pe_ratio, debt_ebitda
            )

            # Update or add analysis for this stock
            found = False
            for idx, stock in enumerate(st.session_state.analyzed_stocks):
                if stock["Ticker"] == ticker:
                    st.session_state.analyzed_stocks[idx] = {
                        "Ticker": ticker,
                        "Rev Growth (%)": revenue_growth,
                        "Earnings Growth (%)": earnings_growth,
                        "P/E": pe_ratio,
                        "Debt/EBITDA": debt_ebitda,
                        "Recommendation": recommendation
                    }
                    found = True
                    break

            if not found:
                st.session_state.analyzed_stocks.append({
                    "Ticker": ticker,
                    "Rev Growth (%)": revenue_growth,
                    "Earnings Growth (%)": earnings_growth,
                    "P/E": pe_ratio,
                    "Debt/EBITDA": debt_ebitda,
                    "Recommendation": recommendation
                })

            analyzed_indices.add(i)
            st.rerun()  # Refresh to show updated results
        else:
            st.warning("Please enter a ticker symbol")

# 3. Results
if st.session_state.analyzed_stocks:
    st.header("📊 Analysis Results")
    st.table(st.session_state.analyzed_stocks)

# Clear results button
if st.session_state.analyzed_stocks:
    if st.button("Clear All Results"):
        st.session_state.analyzed_stocks = []
        st.rerun()