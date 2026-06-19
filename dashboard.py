import streamlit as st
import tushare as ts
import pandas as pd

# ========== 配置 ==========
TOKEN = "46cd2dce6fce352638b4896a90e61a1d7cb69cfe9c63bb90ed823b08"

st.set_page_config(page_title="A股量化选股系统（稳定版）", layout="wide")

st.title("📊 A股量化选股系统（稳定版）")

# ========== 初始化 ==========
@st.cache_data(show_spinner=False)
def init_pro():
    try:
        ts.set_token(TOKEN)
        pro = ts.pro_api()
        return pro
    except Exception as e:
        st.error(f"Tushare初始化失败：{e}")
        return None


# ========== 拉取股票 ==========
@st.cache_data(show_spinner=True)
def get_stock_list():
    pro = init_pro()
    if pro is None:
        return None, "初始化失败"

    try:
        df = pro.stock_basic(exchange='', list_status='L',
                             fields='ts_code,name,industry')

        if df is None or len(df) == 0:
            return None, "Tushare返回空数据（token权限/网络问题）"

        return df, "OK"

    except Exception as e:
        return None, str(e)


# ========== UI ==========
if st.button("🚀 开始A股选股（稳定版）"):

    df, msg = get_stock_list()

    if df is None:
        st.error(f"❌ 数据获取失败：{msg}")
        st.stop()

    st.success(f"✅ 成功获取股票数量：{len(df)}")

    st.dataframe(df.head(20))

    # 简单筛选示例（稳定不会崩）
    st.subheader("🔥 示例筛选：非空行业股票")

    filtered = df.dropna(subset=["industry"])
    st.dataframe(filtered.head(20))
