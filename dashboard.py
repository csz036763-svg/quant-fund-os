import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np

st.set_page_config(page_title="A股量化选股系统（稳定版）", layout="wide")

st.title("📊 A股量化选股系统（稳定生产版）")
st.caption("基于AKShare · 无需Token · 自动全市场扫描")

# =========================
# 获取股票池（稳定源）
# =========================
@st.cache_data(ttl=3600)
def get_stock_pool():
    df = ak.stock_info_a_code_name()
    df.columns = ["代码", "名称"]
    return df

# =========================
# 获取行情数据（稳定版）
# =========================
@st.cache_data(ttl=300)
def get_market_data():
    df = ak.stock_zh_a_spot_em()
    return df

# =========================
# 简化多因子评分模型
# =========================
def score_stock(df):
    df = df.copy()

    # 转换数值
    for col in ["涨跌幅", "换手率", "量比"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 简化评分模型（稳定版）
    df["评分"] = (
        df.get("涨跌幅", 0) * 2 +
        df.get("换手率", 0) * 1.5 +
        df.get("量比", 0) * 3
    )

    return df

# =========================
# UI
# =========================
if st.button("🚀 开始全市场选股（稳定版）"):

    try:
        with st.spinner("正在获取A股全市场数据..."):

            df = get_market_data()

            if df is None or df.empty:
                st.error("❌ 数据为空（可能是AKShare网络波动）")
                st.stop()

            st.success(f"✅ 获取成功：{len(df)}只股票")

            df = score_stock(df)

            # 排序选股
            df = df.sort_values("评分", ascending=False)

            top = df.head(50)

            st.subheader("🔥 Top 50股票池")

            show_cols = ["代码", "名称", "最新价", "涨跌幅", "换手率", "量比", "评分"]

            exist_cols = [c for c in show_cols if c in top.columns]

            st.dataframe(top[exist_cols], use_container_width=True)

            st.subheader("📈 Top10可视化")

            chart_data = top.head(10).set_index("名称")["评分"]
            st.bar_chart(chart_data)

    except Exception as e:
        st.error(f"系统异常：{str(e)}")

# =========================
# Debug区
# =========================
with st.expander("🔧 Debug信息"):
    try:
        st.write("股票池测试：")
        st.write(get_stock_pool().head())

        st.write("市场数据测试：")
        st.write(get_market_data().head())

    except Exception as e:
        st.error(str(e))
