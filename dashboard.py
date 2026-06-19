import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="量化选股系统 V3", layout="wide")

st.title("📊 A股 / 美股 专业量化选股系统 V3")

# =========================
# 输入
# =========================
symbol = st.text_input("输入股票代码（AAPL / TSLA / 000001.SS）", "AAPL")

# =========================
# 数据获取
# =========================
@st.cache_data
def get_data(symbol):
    try:
        df = yf.download(symbol, period="1y")
        return df
    except:
        return pd.DataFrame()

df = get_data(symbol)

# =========================
# 数据检查（防崩关键）
# =========================
if df is None or df.empty:
    st.error("❌ 数据获取失败：请检查股票代码或网络")
    st.stop()

# =========================
# 技术指标
# =========================
df["MA5"] = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()

# RSI
delta = df["Close"].diff()
gain = np.where(delta > 0, delta, 0)
loss = np.where(delta < 0, -delta, 0)

gain = pd.Series(gain).rolling(14).mean()
loss = pd.Series(loss).rolling(14).mean()

rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))

# MACD
ema12 = df["Close"].ewm(span=12).mean()
ema26 = df["Close"].ewm(span=26).mean()
df["MACD"] = ema12 - ema26
df["Signal"] = df["MACD"].ewm(span=9).mean()

# =========================
# 量化评分系统 V3
# =========================
score = 50

# 均线
if df["MA5"].iloc[-1] > df["MA20"].iloc[-1]:
    score += 15
else:
    score -= 10

# RSI
if df["RSI"].iloc[-1] < 30:
    score += 15
elif df["RSI"].iloc[-1] > 70:
    score -= 15

# MACD
if df["MACD"].iloc[-1] > df["Signal"].iloc[-1]:
    score += 15
else:
    score -= 5

score = max(0, min(100, score))

# =========================
# 输出评分
# =========================
st.subheader("📌 量化评分")
st.metric("综合评分", f"{score}/100")

if score >= 75:
    st.success("🟢 强烈关注 / 潜在买入")
elif score >= 50:
    st.warning("🟡 观望 / 震荡区间")
else:
    st.error("🔴 回避 / 风险较高")

# =========================
# K线图
# =========================
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="K线"
))

fig.add_trace(go.Scatter(x=df.index, y=df["MA5"], name="MA5"))
fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="MA20"))

fig.update_layout(height=600, title="K线 + 均线系统")
st.plotly_chart(fig, use_container_width=True)

# =========================
# RSI
# =========================
st.subheader("RSI指标")
st.line_chart(df["RSI"])

# =========================
# MACD
# =========================
st.subheader("MACD指标")
st.line_chart(df[["MACD", "Signal"]])

# =========================
# 数据表
# =========================
with st.expander("📊 查看原始数据"):
    st.dataframe(df.tail(30))
