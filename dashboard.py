import streamlit as st
import numpy as np
import pandas as pd

st.title("🏦 AI Quant Fund Cloud")

data = np.cumsum(np.random.randn(100)) + 100

st.metric("Fund Value", f"{data[-1]:.2f}")

st.line_chart(data)
