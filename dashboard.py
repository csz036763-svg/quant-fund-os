import streamlit as st
import pandas as pd
import numpy as np
import akshare as ak
import time

# =========================
# 页面标题
# =========================
st.title("📊 A股量化选股系统（稳定版）")

st.write("基于多因子模型的A股选股系统（云端稳定版）")

# =========================
# 1. 稳定获取股票列表（防崩核心）
# =========================
@st.cache_data(ttl=3600)
def get_stock_list():
    try:
        df = ak.stock_info_a_code_name()
        if df is None or len(df) == 0:
            raise Exception("empty data")
        return df
    except:
        try:
            df = ak.stock_info_sh_name_code("主板A股")
            return df
        except:
            # 最终兜底（保证永不崩）
            return pd.DataFrame({
                "code": ["000001", "000002", "600000", "600036", "601318"],
                "name": ["平安银行", "万科A", "浦发银行", "招商银行", "中国平安"]
            })

# =========================
# 2. 获取行情数据（防崩）
# =========================
@st.cache_data(ttl=300)
def get_stock_data(symbol):
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        if df is None or len(df) < 30:
            return None

        df = df.tail(60)

        # 统一字段
        df = df.rename(columns={
            "收盘": "close",
            "成交量": "volume"
        })

        return df

    except:
        return None

# =========================
# 3. 因子评分模型
# =========================
def calculate_score(df):
    try:
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma20"] = df["close"].rolling(20).mean()

        # 动量
        momentum = df["close"].iloc[-1] / df["close"].iloc[-20] - 1

        # 趋势
        trend = 1 if df["ma5"].iloc[-1] > df["ma20"].iloc[-1] else 0

        # 量能
        vol_ratio = df["volume"].iloc[-1] / df["volume"].mean()

        # 综合评分
        score = momentum * 0.6 + trend * 0.3 + vol_ratio * 0.1

        return score

    except:
        return None

# =========================
# 4. UI
# =========================
stocks = get_stock_list()

st.write(f"📌 股票池数量：{len(stocks)}")

# =========================
# 5. 扫描按钮
# =========================
if st.button("🚀 开始A股选股（稳定版）"):

    results = []

    # 🔥 限制数量防止云端崩
    sample_size = min(80, len(stocks))
    sample = stocks.sample(sample_size)

    progress = st.progress(0)

    for i, row in enumerate(sample.iterrows()):
        try:
            code = row[1]["code"] if "code" in stocks.columns else row[1][0]
            name = row[1]["name"] if "name" in stocks.columns else "Unknown"

            df = get_stock_data(code)

            if df is None:
                continue

            score = calculate_score(df)

            if score is not None:
                results.append({
                    "code": code,
                    "name": name,
                    "score": round(score, 4)
                })

        except:
            continue

        progress.progress((i + 1) / sample_size)
        time.sleep(0.15)  # 防止被封 / 防止崩溃

    # =========================
    # 6. 输出结果
    # =========================
    if len(results) > 0:

        result_df = pd.DataFrame(results)
        result_df = result_df.sort_values("score", ascending=False)

        st.subheader("🏆 Top 10 推荐股票")
        st.dataframe(result_df.head(10))

        st.subheader("📊 全部评分结果")
        st.dataframe(result_df)

    else:
        st.warning("暂无有效数据，请稍后重试")
