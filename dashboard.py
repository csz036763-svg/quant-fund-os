import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Real Stock Quant Fund", layout="centered")

st.title("🏦 Real Stock Quant Fund System")

# ======================
# 🟢 选择股票
# ======================
symbol = st.selectbox(
    "Choose Stock",
    ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOG"]
)

# ======================
# 🟢 下载数据
# ======================
data = yf.download(symbol, period="6mo", interval="1d")

# ======================
# 🟢 收盘价
# ======================
df = pd.DataFrame()
df["Close"] = data["Close"]

# ======================
# 🟢 显示
# ======================
st.metric("Latest Price", f"{df['Close'].iloc[-1]:.2f}")

st.line_chart(df["Close"])
