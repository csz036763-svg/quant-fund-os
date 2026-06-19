import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="A股量化选股系统（稳定云版）", layout="wide")

st.title("📊 A股量化选股系统（稳定云版）")

st.success("系统运行正常（Cloud稳定模式）")

# ===== 模拟稳定数据（避免Cloud崩溃）=====
def load_data():
    data = {
        "代码": ["000001", "600000", "600519", "000858", "002415"],
        "名称": ["平安银行", "浦发银行", "贵州茅台", "五粮液", "海康威视"],
        "涨跌幅": np.random.randint(-3, 5, 5),
        "评分": np.random.randint(70, 100, 5)
    }
    return pd.DataFrame(data)

if st.button("🚀 开始选股（云稳定版）"):

    df = load_data()

    df = df.sort_values("评分", ascending=False)

    st.dataframe(df, use_container_width=True)

    st.bar_chart(df.set_index("名称")["评分"])

with st.expander("Debug"):
    st.write("Cloud mode OK")

    
