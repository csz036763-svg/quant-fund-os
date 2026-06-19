import streamlit as st

from data.data_loader import load_data
from strategy.multi_factor_v3 import score_stocks
from backtest.engine_v3 import backtest

st.set_page_config(page_title="量化V3系统", layout="wide")

st.title("🚀 A股量化选股系统 V3（专业版）")

st.markdown("系统状态：🟢 正常运行")

if st.button("🔥 开始全市场选股"):

    df = load_data()

    result = score_stocks(df)

    st.subheader("📊 股票池（排序后）")
    st.dataframe(result, use_container_width=True)

    st.subheader("🔥 Top10股票")
    st.bar_chart(result.head(10).set_index("名称")["score"])

    st.subheader("📈 回测结果")
    st.json(backtest(result))
