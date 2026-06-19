import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Real Stock Quant Fund", layout="centered")

st.title("🏦 Real Stock Quant Fund System")

symbol = st.selectbox(
    "Choose Stock",
    ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOG"]
)

data = yf.download(symbol, period="6mo", interval="1d")

if data is None or data.empty:
    st.error("⚠️ No data received from yfinance. Please try another stock.")
    st.stop()

df = pd.DataFrame()
df["Close"] = data["Close"]

if df["Close"].dropna().empty:
    st.error("⚠️ Close price data is empty.")
    st.stop()

latest_price = df["Close"].dropna().iloc[-1]

st.metric("Latest Price", f"{latest_price:.2f}")

st.line_chart(df["Close"])
