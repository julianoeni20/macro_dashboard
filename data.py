def get_us_yield(lookback):

  from fredapi import Fred
  import pandas as pd

  fred = Fred(api_key='f6c7b45610d142d607396b4207eb091a')

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