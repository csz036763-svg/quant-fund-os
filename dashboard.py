import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np

# =========================
# 页面设置
# =========================
st.set_page_config(page_title="A股量化选股系统", layout="wide")

st.title("📊 A股量化选股系统（稳定专业版）")

# =========================
# 股票池（防崩版）
# =========================
@st.cache_data
def get_stock_list():
    try:
        df = ak.stock_info_a_code_name()
        df = df.dropna()
        return df["code"].tolist()
    except:
        return []

# =========================
# 数据获取（稳定核心）
# =========================
def get_stock_data(symbol):
    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            adjust="qfq"
        )

        if df is None or df.empty:
            return None

        df = df.rename(columns={
            "收盘": "close",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "成交量": "volume"
        })

        if "close" not in df.columns:
            return None

        df = df.tail(60)
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df = df.dropna()

        if len(df) < 30:
            return None

        return df

    except:
        return None

# =========================
# 因子模型（稳定版）
# =========================
def score_stock(df):
    try:
        close = df["close"]

        momentum = close.iloc[-1] / close.iloc[0] - 1
        ma20 = close.rolling(20).mean().iloc[-1]
        ma_factor = close.iloc[-1] / ma20 - 1
        volatility = close.pct_change().std()

        score = 0.5 * momentum + 0.3 * ma_factor - 0.2 * volatility
        return score

    except:
        return None

# =========================
# 全市场选股（稳定版）
# =========================
def run_screen(limit=20):
    stocks = get_stock_list()

    if not stocks:
        return []

    results = []

    progress = st.progress(0)
    total = min(200, len(stocks))  # 防崩关键

    for i, code in enumerate(stocks[:total]):
        df = get_stock_data(code)

        if df is None:
            continue

        score = score_stock(df)

        if score is None:
            continue

        results.append((code, score))

        progress.progress((i + 1) / total)

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:limit]

# =========================
# UI
# =========================
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 开始A股选股（稳定版）"):
        with st.spinner("正在扫描A股市场..."):
            results = run_screen()

        if not results:
            st.warning("暂无有效数据（可能是网络限制或AKShare接口波动）")
        else:
            st.success("选股完成！")

            df_show = pd.DataFrame(results, columns=["股票代码", "评分"])
            st.dataframe(df_show, use_container_width=True)

with col2:
    st.info("📌 系统说明：\n- 使用AKShare\n- 多因子评分模型\n- 自动过滤无效数据\n- 限制200只股票防止崩溃")
