import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Multi-Asset Quant Fund", layout="centered")

st.title("🏦 Multi-Stock Quant Fund System")

# ======================
# 股票池
# ======================
symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]

st.write("📊 Portfolio Assets:", symbols)

# ======================
# 权重（等权）
# ======================
weight = 1 / len(symbols)

# ======================
# 组合收益
# ======================
portfolio_returns = None

for symbol in symbols:

    data = yf.download(symbol, period="6mo", interval="1d")

    if data.empty:
        continue

    df = pd.DataFrame()
    df["Close"] = data["Close"]

    # ===== 策略 =====
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    df["Signal"] = 0
    df.loc[df["MA5"] > df["MA20"], "Signal"] = 1

    df["Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Return"] * df["Signal"].shift(1)

    if portfolio_returns is None:
        portfolio_returns = df["Strategy_Return"] * weight
    else:
        portfolio_returns = portfolio_returns.add(df["Strategy_Return"] * weight, fill_value=0)

# ======================
# 累计收益
# ======================
portfolio_returns = portfolio_returns.fillna(0)

cumulative = (1 + portfolio_returns).cumprod()

# ======================
# 展示
# ======================
st.metric("Portfolio Latest Value", f"{cumulative.iloc[-1]:.2f}")

st.subheader("📈 Portfolio Growth Curve")
st.line_chart(cumulative)

st.subheader("📊 Strategy Info")
st.write("Equal-weight MA strategy portfolio")
