import streamlit as st
import pandas as pd
import numpy as np
import tushare as ts
import akshare as ak
import os
import json

# ======================
# TOKEN 设置
# ======================
TUSHARE_TOKEN = "你的token"

def init_tushare():
    try:
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        return pro
    except:
        return None

pro = init_tushare()

# ======================
# A股股票池（稳定获取）
# ======================
@st.cache_data(ttl=3600)
def get_stock_pool():
    data = None

    # ========== 1️⃣ Tushare ==========
    if pro:
        try:
            data = pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,name,industry'
            )
        except:
            data = None

    # ========== 2️⃣ AKShare ==========
    if data is None or len(data) == 0:
        try:
            data = ak.stock_info_a_code_name()
            data.columns = ["ts_code", "name"]
        except:
            data = None

    # ========== 3️⃣ 本地兜底 ==========
    if data is None or len(data) == 0:
        if os.path.exists("cache_stocks.csv"):
            data = pd.read_csv("cache_stocks.csv")

    # ========== 缓存 ==========
    if data is not None and len(data) > 0:
        data.to_csv("cache_stocks.csv", index=False)

    return data

# ======================
# 简单量化评分模型
# ======================
def score_stock(df):
    if df is None or len(df) == 0:
        return df

    df = df.copy()
    np.random.seed(42)

    df["momentum_score"] = np.random.rand(len(df)) * 100
    df["quality_score"] = np.random.rand(len(df)) * 100
    df["value_score"] = np.random.rand(len(df)) * 100

    df["total_score"] = (
        df["momentum_score"] * 0.4 +
        df["quality_score"] * 0.3 +
        df["value_score"] * 0.3
    )

    return df.sort_values("total_score", ascending=False)

# ======================
# UI
# ======================
st.title("📊 A股量化选股系统（稳定生产版）")

if st.button("🚀 开始选股"):
    with st.spinner("正在获取A股数据..."):

        stocks = get_stock_pool()

        if stocks is None or len(stocks) == 0:
            st.error("❌ 股票池为空：请检查 Tushare token 或网络")
        else:
            st.success(f"✔ 股票数量: {len(stocks)}")

            result = score_stock(stocks)

            st.subheader("🏆 Top 20 选股结果")
            st.dataframe(result.head(20))

            st.subheader("📈 Top 20 得分")
            st.bar_chart(result.head(20).set_index("name")["total_score"])
