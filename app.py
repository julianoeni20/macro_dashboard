import streamlit as st
from plots import us_treasury_plots

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

if check_password():
    
    st.title("FBU Macro Dashboard")

    with st.spinner("Fetching latest market data..."):
        fig_ts, fig_curve = us_treasury_plots()

    st.plotly_chart(fig_ts)
    st.plotly_chart(fig_curve)