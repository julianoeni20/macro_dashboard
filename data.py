import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def get_us_yield(lookback):

    from fredapi import Fred
    import pandas as pd
    import streamlit as st

    fred_key = st.secrets["fredapikey"]
    fred = Fred(api_key=fred_key)

    us_yields = {
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

def get_recent_releases():

    from fredapi import Fred
    import streamlit as st

    fred_key = st.secrets["fredapikey"]
    fred = Fred(api_key=fred_key)

    fred = Fred(api_key=st.secrets["FRED_API_KEY"])
    # Get the 10 most recent economic releases
    releases = fred.get_releases(limit=10, order_by='press_release_date', sort_order='desc')
    return releases[['name', 'press_release_date']]