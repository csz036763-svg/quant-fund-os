import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Quant Strategy Fund", layout="centered")

st.title("🏦 Quant Fund Strategy System")

# ======================
# 选择股票
# ======================
symbol = st.selectbox(
    "Choose Stock",
    ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOG"]
)

# ======================
# 下载数据
# ======================
data = yf.download(symbol, period="6mo", interval="1d")

if data.empty:
    st.error("No data loaded")
    st.stop()

df = pd.DataFrame()
df["Close"] = data["Close"]

# ======================
# 均线策略
# ======================
df["MA5"] = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()

df["Signal"] = 0
df.loc[df["MA5"] > df["MA20"], "Signal"] = 1
df.loc[df["MA5"] <= df["MA20"], "Signal"] = 0

df["Position"] = df["Signal"].diff()

# ======================
# 收益计算
# ======================
df["Return"] = df["Close"].pct_change()
df["Strategy_Return"] = df["Return"] * df["Signal"].shift(1)

df["Cumulative_Market"] = (1 + df["Return"]).cumprod()
df["Cumulative_Strategy"] = (1 + df["Strategy_Return"]).cumprod()

# ======================
# 最新价格
# ======================
st.metric("Latest Price", f"{df['Close'].iloc[-1]:.2f}")

# ======================
# 图1：价格 + 均线
# ======================
st.subheader("📈 Price & Moving Averages")
st.line_chart(df[["Close", "MA5", "MA20"]])

# ======================
# 图2：策略收益
# ======================
st.subheader("📊 Strategy vs Market")

st.line_chart(df[["Cumulative_Market", "Cumulative_Strategy"]])

# ======================
# 信号展示
# ======================
st.subheader("📍 Latest Signal")

last_signal = df["Signal"].iloc[-1]

if last_signal == 1:
    st.success("🟢 BUY Signal (MA5 > MA20)")
else:
    st.warning("🔴 SELL Signal (MA5 <= MA20)")

