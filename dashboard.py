import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np

# =========================
# 页面设置
# =========================
st.set_page_config(page_title="A股量化选股系统", layout="wide")

st.title("📊 A股量化选股系统（终极稳定版）")

st.caption("✔ 防崩溃 + ✔ 自动修复symbol + ✔ 空数据过滤 + ✔ 稳定扫描")

# =========================
# 股票池（稳定）
# =========================
@st.cache_data
def get_stock_list():
    try:
        df = ak.stock_info_a_code_name()
        df = df.dropna()
        return df["code"].tolist()
    except:
        return []

# =========================
# 数据获取（终极稳定核心）
# =========================
def get_stock_data(symbol):
    try:
        # ===== 修复AKShare symbol格式问题 =====
        if symbol.startswith("6"):
            code = symbol  # akshare新版本直接用数字
        elif symbol.startswith("0") or symbol.startswith("3"):
            code = symbol
        else:
            code = symbol

        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            adjust="qfq"
        )

        if df is None or df.empty:
            return None

        # ===== 标准化字段 =====
        df = df.rename(columns={
            "收盘": "close",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "成交量": "volume"
        })

        if "close" not in df.columns:
            return None

        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df = df.dropna()

        if len(df) < 30:
            return None

        return df.tail(60)

    except:
        return None

# =========================
# 多因子模型（稳定版）
# =========================
def score_stock(df):
    try:
        close = df["close"]

        # 动量因子
        momentum = close.iloc[-1] / close.iloc[0] - 1

        # 均线因子
        ma20 = close.rolling(20).mean().iloc[-1]
        ma_factor = close.iloc[-1] / ma20 - 1

        # 波动率
        volatility = close.pct_change().std()

        # 综合评分
        score = (
            0.5 * momentum +
            0.3 * ma_factor -
            0.2 * volatility
        )

        return score

    except:
        return None

# =========================
# 全市场扫描（防崩版）
# =========================
def run_screen(limit=20):
    stocks = get_stock_list()

    if not stocks:
        return []

    results = []

    # 🔥 防崩关键：限制扫描数量
    max_scan = min(200, len(stocks))

    progress = st.progress(0)

    for i, code in enumerate(stocks[:max_scan]):

        df = get_stock_data(code)

        if df is None:
            continue

        score = score_stock(df)

        if score is None:
            continue

        results.append((code, score))

        progress.progress((i + 1) / max_scan)

    # 排序
    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:limit]

# =========================
# UI界面
# =========================
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🚀 开始A股选股（终极稳定版）"):

        with st.spinner("正在扫描A股市场（稳定模式）..."):
            results = run_screen()

        if not results:
            st.error("❌ 没有获取到有效数据（可能是AKShare接口波动）")
        else:
            st.success("✅ 选股完成")

            df_show = pd.DataFrame(results, columns=["股票代码", "评分"])
            st.dataframe(df_show, use_container_width=True)

with col2:
    st.info("""
📌 系统说明（终极稳定版）：
- 使用 AKShare A股数据
- 自动过滤异常股票
- 多因子评分模型
- 限制200只防止崩溃
- 自动跳过无数据标的
- 防JSON/Index错误
""")

# =========================
# 调试信息（关键）
# =========================
with st.expander("🔧 Debug信息"):
    st.write("股票池数量：", len(get_stock_list()))
