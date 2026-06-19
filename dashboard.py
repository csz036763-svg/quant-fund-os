import streamlit as st
import tushare as ts
import pandas as pd
import numpy as np

st.set_page_config(page_title="A股量化选股系统（稳定版）", layout="wide")

st.title("📊 A股量化选股系统（稳定生产版）")

# ========== TOKEN ==========
TOKEN = "你的tushare token"
ts.set_token(TOKEN)
pro = ts.pro_api()

# ========== 安全函数 ==========
def safe_call(func, **kwargs):
    try:
        df = func(**kwargs)
        if df is None or len(df) == 0:
            return pd.DataFrame()
        return df
    except Exception as e:
        st.warning(f"数据获取失败: {str(e)}")
        return pd.DataFrame()

# ========== 获取股票池 ==========
@st.cache_data
def get_stock_pool():
    df = safe_call(pro.stock_basic, exchange='', list_status='L')
    if df.empty:
        return []
    
    df = df[~df['name'].str.contains('ST')]
    return df['ts_code'].tolist()[:500]  # 防止爆接口

# ========== 获取行情 ==========
def get_daily(ts_code):
    df = safe_call(pro.daily, ts_code=ts_code, limit=60)
    return df

# ========== 因子 ==========
def score_stock(df):
    if df.empty or len(df) < 20:
        return None
    
    try:
        close = df['close']
        ret = close.iloc[-1] / close.iloc[0] - 1
        vol = df['vol'].mean()
        score = ret * 100 / (vol + 1)
        return score
    except:
        return None

# ========== 主逻辑 ==========
if st.button("🚀 开始A股选股（稳定版）"):

    pool = get_stock_pool()
    
    if len(pool) == 0:
        st.error("股票池为空，请检查Tushare token")
        st.stop()

    result = []

    progress = st.progress(0)

    for i, code in enumerate(pool):

        df = get_daily(code)
        score = score_stock(df)

        if score is not None:
            result.append((code, score))

        progress.progress((i + 1) / len(pool))

    if len(result) == 0:
        st.error("无有效数据")
        st.stop()

    result = sorted(result, key=lambda x: x[1], reverse=True)

    top = pd.DataFrame(result[:20], columns=["股票代码", "评分"])

    st.subheader("🏆 Top20推荐股票")
    st.dataframe(top)
