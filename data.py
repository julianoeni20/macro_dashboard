import ssl
import pandas as pd
import requests
import streamlit as st
from datetime import date, timedelta
from fredapi import Fred
import yfinance as yf
ssl._create_default_https_context = ssl._create_unverified_context

@st.cache_data(ttl=3600)

def get_us_yield(lookback):

    fred_key = st.secrets["fredapikey"]
    fred = Fred(api_key=fred_key)

    us_yields = {
        "US1M": "DTB1",
        "US3M": "DTB3",
        "US1Y": "DGS1",
        "US2Y": "DGS2",
        "US5Y": "DGS5",
        "US10Y": "DGS10",
        "US20Y": "DGS20"
    }

    fred_data = {}
    for name, series_id in us_yields.items():
        data = fred.get_series(series_id)
        fred_data[name] = data.tail(lookback)
    df = pd.DataFrame(fred_data).ffill()
    return df


IMPORTANT_KEYWORDS = [
    "Gross Domestic Product",           # GDP
    "Consumer Price Index",             # CPI
    "Employment Situation",             # Non-farm payrolls & Unemployment
    "Producer Price Index",             # PPI
    "Personal Income and Outlays",      # PCE Inflation (The Fed's favorite)
    "Retail and Food Services",         # Retail Sales
    "New Residential Construction",     # Housing Starts
    "Industrial Production",
    "International Trade",              # Trade Balance
    "FOMC",                             # Fed Meetings (if available)
    "Beige Book"
]

def get_upcoming_releases(api_key, days_ahead=7, only_important=True):
    """
    Fetches upcoming releases and optionally filters for high-impact events.
    """
    url = "https://api.stlouisfed.org/fred/releases/dates"
    today = date.today()
    future_limit = today + timedelta(days=days_ahead)
    
    params = {
        'api_key': api_key,
        'file_type': 'json',
        'include_release_dates_with_no_data': 'true',
        'realtime_start': today.strftime('%Y-%m-%d'),
        'limit': 100,
        'sort_order': 'asc'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'release_dates' in data:
            df = pd.DataFrame(data['release_dates'])
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # 1. Date Filter
            mask = (df['date'] >= today) & (df['date'] <= future_limit)
            future_df = df.loc[mask].copy()
            
            # 2. Importance Filter (The new part)
            if only_important and not future_df.empty:
                # Create a regex pattern to match any of the keywords
                pattern = '|'.join(IMPORTANT_KEYWORDS)
                future_df = future_df[
                    future_df['release_name'].str.contains(pattern, case=False, regex=True)
                ]
            
            return future_df[['date', 'release_name', 'release_id']].sort_values('date')
        
        return pd.DataFrame()
        
    except Exception as e:
        print(f"FRED API Error: {e}")
        return pd.DataFrame()
    
def get_us_credit(lookback=1500):
    """
    Fetches ICE BofA Option-Adjusted Spreads (OAS).
    Returns a DataFrame of the last 'lookback' trading days.
    """
    try:
        fred_key = st.secrets["fredapikey"]
        fred = Fred(api_key=fred_key)

        # Correct Tickers for ICE BofA Spreads
        us_yields = {
            "High Yield (Junk)": "BAMLH0A0HYM2",
            "BBB Corp (Inv. Grade)": "BAMLC0A4CBBB",
            "AAA Corp (Prime)": "BAMLC0A1CAAA",
        }

        fred_data = {}
        for name, series_id in us_yields.items():
            # Fetch all data first
            fred_data[name] = fred.get_series(series_id)
            
        # Combine into DataFrame to align dates automatically
        df = pd.DataFrame(fred_data).ffill()
        
        # Return the last N days
        return df.tail(lookback)

    except Exception as e:
        st.error(f"Error fetching credit data: {e}")
        return pd.DataFrame()
    
def get_earnings_dates():

    calendars = yf.Calendars()
    start_date = date.today()
    end_date = start_date + timedelta(days=7)

    df = calendars.get_earnings_calendar(market_cap=300000000, limit=100, start=start_date, end=end_date)
    df = df.reset_index()
    df['Earnings Date'] = pd.to_datetime(df['Event Start Date']).dt.date
    df = df.sort_values('Earnings Date')

    return df[['Symbol', 'Company', 'Event Name', 'Earnings Date', 'EPS Estimate', 'Reported EPS', 'Surprise(%)']]


