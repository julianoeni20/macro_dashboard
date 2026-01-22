import streamlit as st
from plots import us_treasury_plots

st.title("FBU Macro Dashboard")

with st.spinner("Fetching latest market data..."):
    fig_ts, fig_curve = us_treasury_plots()

st.plotly_chart(fig_ts)
st.plotly_chart(fig_curve)