import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="量化选股V2", layout="wide")

st.title("📊 A股/美股量化选股系统 V2")

# ===== 输入股票 =====
symbol = st.text_input("输入股票代码（AAPL / TSLA / 000001.SS）", "AAPL")

# ===== 下载数据 =====
@st.cache_data
def load_data(symbol):
    df = yf.download(symbol, period="6mo")
    return df

if symbol:
    df = load_data(symbol)

    if df.empty:
        st.error("⚠️ 没有获取到数据，请检查代码")
    else:
        # ===== 技术指标 =====
        df["MA5"] = df["Close"].rolling(5).mean()
        df["MA20"] = df["Close"].rolling(20).mean()

        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # ===== MACD =====
        ema12 = df["Close"].ewm(span=12).mean()
        ema26 = df["Close"].ewm(span=26).mean()
        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9).mean()

        # ===== 评分系统 =====
        score = 50

        if df["MA5"].iloc[-1] > df["MA20"].iloc[-1]:
            score += 10
        else:
            score -= 10

        if df["RSI"].iloc[-1] < 30:
            score += 10
        elif df["RSI"].iloc[-1] > 70:
            score -= 10

        if df["MACD"].iloc[-1] > df["Signal"].iloc[-1]:
            score += 10
        else:
            score -= 5

        score = max(0, min(100, score))

        # ===== 展示评分 =====
        st.subheader("📌 选股评分")
        st.metric("综合评分", f"{score}/100")

        # ===== 买卖信号 =====
        if score > 70:
            st.success("🟢 信号：建议关注/买入")
        elif score < 40:
            st.error("🔴 信号：建议回避/卖出")
        else:
            st.warning("🟡 信号：震荡/观望")

        # ===== K线图 =====
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

        fig.update_layout(height=600, title="K线 + 均线")
        st.plotly_chart(fig, use_container_width=True)

        # ===== RSI =====
        st.subheader("RSI")
        st.line_chart(df["RSI"])

        # ===== MACD =====
        st.subheader("MACD")
        st.line_chart(df[["MACD", "Signal"]])
