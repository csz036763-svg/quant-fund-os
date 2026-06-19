import streamlit as st
import tushare as ts
import pandas as pd

# =========================
# 🔧 基础配置
# =========================
st.set_page_config(page_title="A股量化选股系统（稳定版）", layout="wide")

st.title("📊 A股量化选股系统（稳定生产版）")

# ⚠️ 你的 token（已强制写入）
TOKEN = "46cd2dce6fce352638b4896a90e61a1d7cb69c63bb90ed823b08"

# =========================
# 🚀 初始化Tushare（关键修复）
# =========================
try:
    pro = ts.pro_api(TOKEN)
except Exception as e:
    st.error(f"Tushare初始化失败：{e}")
    st.stop()

# =========================
# 🛡️ 安全调用函数（防崩）
# =========================
def safe_call(func, **kwargs):
    try:
        df = func(**kwargs)
        if df is None or len(df) == 0:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()

# =========================
# 📦 股票池
# =========================
@st.cache_data
def get_stock_pool():
    df = safe_call(pro.stock_basic, exchange='', list_status='L')

    if df.empty:
        return []

    # 去ST + 去空值
    df = df[~df['name'].str.contains('ST', na=False)]

    return df['ts_code'].tolist()

# =========================
# 📈 行情数据
# =========================
def get_daily(ts_code):
    df = safe_call(pro.daily, ts_code=ts_code, limit=60)
    return df

# =========================
# 🧠 简单选股因子模型
# =========================
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

# =========================
# 🚀 主程序
# =========================
if st.button("🚀 开始A股选股（稳定版）"):

    pool = get_stock_pool()

    if len(pool) == 0:
        st.error("股票池为空：请检查Tushare权限或token")
        st.stop()

    result = []

    progress = st.progress(0)

    for i, code in enumerate(pool[:200]):  # 🔥 限制200只防止崩溃

        df = get_daily(code)
        score = score_stock(df)

        if score is not None:
            result.append((code, score))

        progress.progress((i + 1) / min(len(pool), 200))

    if len(result) == 0:
        st.error("无有效数据（API可能限流）")
        st.stop()

    result = sorted(result, key=lambda x: x[1], reverse=True)

    top = pd.DataFrame(result[:20], columns=["股票代码", "评分"])

    st.subheader("🏆 Top20选股结果（稳定版）")
    st.dataframe(top)
