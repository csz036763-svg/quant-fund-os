import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("🏦 Institutional Multi-Asset Fund (NAV Model)")

symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]

weights = np.array([0.2]*len(symbols))

price_data = pd.DataFrame()

# ======================
# 下载数据
# ======================
for s in symbols:
    df = yf.download(s, period="6mo")["Close"]
    price_data[s] = df

# ======================
# 处理缺失值
# ======================
price_data = price_data.dropna()

# ======================
# 收益率
# ======================
returns = price_data.pct_change().dropna()

# ======================
# 组合收益（真实基金算法）
# ======================
portfolio_return = returns.dot(weights)

# ======================
# NAV曲线
# ======================
nav = (1 + portfolio_return).cumprod()

# ======================
# 展示
# ======================
st.write("📊 Assets:", symbols)

st.metric("Fund NAV", f"{nav.iloc[-1]:.2f}")

st.line_chart(nav)
   
