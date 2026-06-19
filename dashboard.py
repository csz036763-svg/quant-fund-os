import streamlit as st
import pandas as pd

st.set_page_config(page_title="A股量化选股系统", layout="wide")

st.title("📊 A股量化选股系统（稳定版）")

st.markdown("### 🚀 系统状态：正常启动")

# ===== 模拟数据（避免空白）=====
def get_stock_data():
    data = {
        "代码": ["000001", "600000", "600519", "000858", "002415"],
        "名称": ["平安银行", "浦发银行", "贵州茅台", "五粮液", "海康威视"],
        "评分": [85, 80, 95, 90, 88],
        "行业": ["银行", "银行", "白酒", "白酒", "安防"]
    }
    return pd.DataFrame(data)

# ===== 按钮 =====
if st.button("🚀 开始选股（稳定版）"):
    try:
        df = get_stock_data()

        if df is None or df.empty:
            st.error("⚠️ 股票池为空")
        else:
            st.success("✅ 选股完成")

            st.dataframe(df, use_container_width=True)

            st.markdown("### 🔥 Top股票")
            st.bar_chart(df.set_index("名称")["评分"])

    except Exception as e:
        st.error(f"系统错误：{str(e)}")

# ===== debug =====
with st.expander("Debug信息"):
    st.write("Python OK")
    st.write("Streamlit OK")
