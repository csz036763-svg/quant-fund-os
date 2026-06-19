import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="量化选股系统 V3", layout="wide")

st.title("📊 A股 / 美股 专业量化选股系统 V3")

# ======================
# 股票池（你可以扩展）
# ======================
stock_pool = [
    "AAPL", "MSFT", "TSLA", "NVDA",
    "000001.SS", "600519.SS", "000858.SS"
]

# ======================
# 下载数据
# ======================
@st.cache_data
def get_data(symbol):
    df = yf.download(symbol, period="1y")
    return df

# ======================
# 单股评分函数
# ======================
def score_stock(df):
    if df is None or df.empty:
        return None

    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    # RSI
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain = pd.Series(gain).rolling(14).mean()
    loss = pd.Series(loss).rolling(14).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    score = 50

    # 均线
    if df["MA5"].iloc[-1] > df["MA20"].iloc[-1]:
        score += 15
    else:
        score -= 10

    # RSI
    if rsi.iloc[-1] < 30:
        score += 15
    elif rsi.iloc[-1] > 70:
        score -= 15

    # MACD
    if macd.iloc[-1] > signal.iloc[-1]:
        score += 15
    else:
        score -= 5

    return max(0, min(100, score))

# ======================
# 扫描股票池
# ======================
if st.button("🔥 开始全市场选股（V3）"):

    result = []

    for stock in stock_pool:
        df = get_data(stock)
        score = score_stock(df)

        if score is not None:
            result.append([stock, score])

    result_df = pd.DataFrame(result, columns=["股票", "评分"])
    result_df = result_df.sort_values("评分", ascending=False)

    st.subheader("📊 选股结果排名")
    st.dataframe(result_df)

    st.bar_chart(result_df.set_index("股票"))
