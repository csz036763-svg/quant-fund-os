import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np

st.title("📊 A股量化选股系统")

# ---------------------------
# 1. 获取股票列表
# ---------------------------
@st.cache_data
def get_stock_list():
    def get_stock_list():
    try:
        # 主方案（可能在云端失败）
        df = ak.stock_info_a_code_name()
        return df
    except:
        try:
            # 备用方案（更稳定）
            df = ak.stock_info_sh_name_code("主板A股")
            return df
        except:
            # 🧨 最终兜底（保证系统永远不崩）
            import pandas as pd
            return pd.DataFrame({
                "code": ["000001", "000002", "600000", "600036"],
                "name": ["平安银行", "万 科A", "浦发银行", "招商银行"]
            })
    return stock_list

stocks = get_stock_list()

st.write("股票数量：", len(stocks))

# ---------------------------
# 2. 获取单只股票数据
# ---------------------------
@st.cache_data
def get_stock_data(symbol):
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        df = df.tail(60)
        df["close"] = df["收盘"]
        df["volume"] = df["成交量"]
        return df
    except:
        return None

# ---------------------------
# 3. 计算因子
# ---------------------------
def calculate_score(df):
    if df is None or len(df) < 20:
        return None

    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()

    momentum = (df["close"].iloc[-1] / df["close"].iloc[-20] - 1)

    trend = 1 if df["ma5"].iloc[-1] > df["ma20"].iloc[-1] else 0

    volume_ratio = df["volume"].iloc[-1] / df["volume"].mean()

    score = momentum * 0.6 + trend * 0.3 + volume_ratio * 0.1

    return score

# ---------------------------
# 4. 扫描股票池（简化版）
# ---------------------------
if st.button("🚀 开始选股"):

    results = []

    sample = stocks.sample(30)  # 先跑30只（避免太慢）

    for _, row in sample.iterrows():
        code = row["code"]

        df = get_stock_data(code)
        score = calculate_score(df)

        if score is not None:
            results.append({
                "code": code,
                "name": row["name"],
                "score": score
            })

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values("score", ascending=False)

    st.subheader("🏆 Top 股票推荐")
    st.dataframe(result_df.head(10))
   
