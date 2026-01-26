import streamlit as st
import pandas as pd

# Local Imports
# Ensure you import get_us_credit from data
from data import get_upcoming_releases, get_us_credit, get_earnings_dates
from plots import us_treasury_plots, credit_spread_plots, plot_ff, plot_indexes

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FBU Macro Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- 2. AUTHENTICATION ---
def check_password():
    """
    Simple password protection.
    """
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# --- 3. UI RENDER FUNCTIONS ---

def render_sidebar():
    """
    Renders the sidebar controls and returns user settings.
    """
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Logout
        if st.button('🔒 Logout', width="stretch"):
            st.session_state["password_correct"] = False
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        
        # Calendar Controls
        st.subheader("Calendar Options")
        days_ahead = st.slider("Days Look Ahead", 1, 60, 14)
        show_important = st.toggle("High Impact Only", value=True)
        
    return days_ahead, show_important

def render_earnings_section():
    """
    Renders the Corporate Earnings section.
    """
    st.subheader("💰 Corporate Earnings Watchlist")
    
    with st.spinner(f"Fetching earnings..."):
        df_earnings = get_earnings_dates()
        
        if not df_earnings.empty:
            st.dataframe(
                df_earnings,
                hide_index=False,
                width="stretch",
                height=400
            )
        else:
            st.info("Could not fetch earnings dates. Markets might be closed or API limited.")

def render_treasury_section():
    """
    Renders the US Treasury Yields section.
    """
    st.subheader("🇺🇸 US Treasury Yields")
    with st.spinner("Fetching Treasury data..."):
        try:
            fig_ts, fig_curve = us_treasury_plots()
            
            # Use columns to display charts side-by-side if space permits
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_ts, width="stretch")
            with col2:
                st.plotly_chart(fig_curve, width="stretch")
        except Exception as e:
            st.error(f"Error loading Treasury data: {e}")

def render_credit_section():
    """
    Renders the Credit Spreads section.
    """
    st.subheader("🏦 Corporate Credit Spreads (OAS)")
    with st.spinner("Fetching Credit data..."):
        try:
            # 1. Fetch Data (Defaults to 1500 days lookback)
            df_credit = get_us_credit()
            
            if not df_credit.empty:
                # 2. Plot Data
                fig = credit_spread_plots(df_credit)
                st.plotly_chart(fig, width="stretch")
                
                # 3. Optional: Raw Data Expander
                with st.expander("View Raw Credit Data"):
                    st.dataframe(df_credit.sort_index(ascending=False).head(50), width="stretch")
            else:
                st.warning("No credit data available.")
        except Exception as e:
            st.error(f"Error loading Credit data: {e}")

def render_fed_futures_section():
    """
    Renders the Fed Funds Futures section.
    """
    st.subheader("🏛️ Fed Funds Futures")
    with st.spinner("Fetching Fed Futures data..."):
        try:
            fig = plot_ff()
            st.plotly_chart(fig, width="stretch")
        except Exception as e:
            st.error(f"Error loading Fed Futures data: {e}")

def render_calendar_section(days_ahead, show_important):
    """
    Renders the Economic Calendar.
    """
    st.divider()
    st.subheader(f"📅 Upcoming Economic Releases (Next {days_ahead} Days)")

    try:
        fred_key = st.secrets["fredapikey"]
        
        # Fetch Data
        df_releases = get_upcoming_releases(fred_key, days_ahead=days_ahead, only_important=show_important)

        if not df_releases.empty:
            st.dataframe(
                df_releases,
                column_config={
                    "date": st.column_config.DateColumn("Date", format="MM-DD-YYYY"),
                    "release_name": "Event / Indicator",
                    "release_id": "Series ID"
                },
                hide_index=True,
                width="stretch",
                height=400 # Fixed height prevents vibration
            )
        else:
            if show_important:
                st.info("No 'High Impact' releases found. Try turning off the filter in the sidebar.")
            else:
                st.info("No releases found.")

    except KeyError:
        st.error("⚠️ FRED API Key not found in secrets.")
    except Exception as e:
        st.error(f"Calendar Error: {e}")

def render_prices():
    """
    Renders the Index Prices tab. Logic is fully encapsulated in plots.py.
    """
    st.divider()
    st.subheader("📊 Global Market Index Prices")

    with st.spinner("Fetching latest market prices..."):
        try:
            # Simply call the function; it handles the list and the download
            fig = plot_indexes()
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to retrieve market data. Please check your connection.")
                
        except Exception as e:
            st.error(f"Error loading Index Prices: {e}")

# --- 4. MAIN APP LOGIC ---

def main():
    if check_password():
        # A. Render Sidebar & Get Settings
        days_ahead, show_important = render_sidebar()

        # B. Header
        st.title("FBU Macro Dashboard")

        # C. Market Data Tabs (Clean layout)
        tab_rates, tab_credit, tab_fed_futures, tab_prices = st.tabs(["Yields & Curve", "Credit Spreads", "Fed Funds Futures", "Prices"])

        with tab_rates:
            render_treasury_section()
        
        with tab_credit:
            render_credit_section()

        with tab_fed_futures:
            render_fed_futures_section()

        with tab_prices:    
            render_prices()
        # D. Economic Calendar
        render_calendar_section(days_ahead, show_important)

        # E. Earnings Section (Optional)
        render_earnings_section()

if __name__ == "__main__":
    main()