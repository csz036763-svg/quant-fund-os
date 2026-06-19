import streamlit as st
import tushare as ts
import pandas as pd

st.set_page_config(page_title="A股量化系统（调试版）", layout="wide")

st.title("📊 A股量化选股系统（DEBUG稳定版）")

# =========================
# ⚠️ TOKEN
# =========================
TOKEN = "46cd2dce6fce352638b4896a90e61a1d7cb69c63bb90ed823b08"

ts.set_token(TOKEN)
pro = ts.pro_api()

# =========================
# 🔍 强制测试API连接（关键）
# =========================
def test_connection():
    try:
        df = pro.stock_basic(exchange='', list_status='L')
        st.write("DEBUG：stock_basic返回行数 =", len(df))
        return df
    except Exception as e:
        st.error("❌ Tushare连接失败")
        st.error(str(e))
        return pd.DataFrame()

# =========================
# 📦 股票池
# =========================
@st.cache_data
def get_stock_pool():
    df = test_connection()

    if df.empty:
        return []

    if 'name' in df.columns:
        df = df[~df['name'].str.contains('ST', na=False)]

    return df['ts_code'].tolist()

# =========================
# 📈 行情数据
# =========================
def get_daily(ts_code):
    try:
        df = pro.daily(ts_code=ts_code, limit=30)
        return df if df is not None else pd.DataFrame()
    except Exception as e:
        st.write(f"{ts_code} error:", e)
        return pd.DataFrame()

# =========================
# 🧠 简单评分
# =========================
def score(df):
    if df is None or df.empty or len(df) < 10:
        return None
    try:
        return df['close'].iloc[-1] / df['close'].iloc[0] - 1
    except:
        return None

# =========================
# 🚀 主程序
# =========================
if st.button("🚀 开始诊断+选股"):

    pool = get_stock_pool()

    st.write("股票池数量 =", len(pool))

    if len(pool) == 0:
        st.error("❌ 股票池为空：不是代码问题，是Tushare没返回数据")
        st.stop()

    results = []
    progress = st.progress(0)

    for i, code in enumerate(pool[:100]):  # 先测100只
        df = get_daily(code)
        s = score(df)

        if s is not None:
            results.append((code, s))

        progress.progress((i + 1) / 100)

    if not results:
        st.error("❌ 无有效行情数据（daily接口失败）")
        st.stop()

    results = sorted(results, key=lambda x: x[1], reverse=True)

    st.subheader("Top 20")
    st.dataframe(pd.DataFrame(results[:20], columns=["code", "score"]))
