STOCK DATA — READ ME FIRST
============================

WHAT'S IN THIS FOLDER
----------------------
18 CSV files, one per stock, covering Jan 2024 - Jan 2026 (daily data).
Columns: Date, Open, High, Low, Close, Volume — exactly what yf.download() gives you.

  IT        -> TCS_NS.csv, INFY_NS.csv, WIPRO_NS.csv
  Banking   -> HDFCBANK_NS.csv, ICICIBANK_NS.csv, SBIN_NS.csv
  Auto      -> TATAMOTORS_NS.csv, MARUTI_NS.csv, MANDM_NS.csv   (M&M -> MANDM in the filename)
  Pharma    -> SUNPHARMA_NS.csv, DRREDDY_NS.csv, CIPLA_NS.csv
  FMCG      -> HINDUNILVR_NS.csv, ITC_NS.csv, NESTLEIND_NS.csv
  Energy    -> RELIANCE_NS.csv, ONGC_NS.csv, NTPC_NS.csv

IMPORTANT — READ THIS
----------------------
This is SYNTHETIC data (realistic fake numbers, not actual market prices).
It behaves like real stock data (Banking/Auto/Energy are more volatile than
FMCG/IT, stocks in the same sector move together) so every pandas operation,
every formula, every plot you build will work exactly the same way it would
on real data. Use this to learn and build the whole pipeline without needing
internet every time.

Before you submit the thesis, swap this for real data — see fetch_real_data.py
below. Takes 2 minutes, one time, and every line of your analysis code stays
identical since the file format is the same.

HOW TO LOAD ONE STOCK
----------------------
    import pandas as pd
    df = pd.read_csv("stock_data/TCS_NS.csv", index_col="Date", parse_dates=True)
    df.head()

No yfinance, no internet, no ticker symbol handling needed — just a normal
file read. This is what fetch_stock() would have handed you, pre-saved.

HOW TO LOAD ALL 18 (when you get to Step 5 — sector grouping)
----------------------------------------------------------------
Build this yourself as planned in the roadmap — don't skip the exercise:

    import os
    folder = "stock_data"
    all_data = {}
    for filename in os.listdir(folder):
        ticker = filename.replace(".csv", "").replace("_", ".", 1)  # rough reverse of the save step
        df = pd.read_csv(os.path.join(folder, filename), index_col="Date", parse_dates=True)
        all_data[ticker] = df

WHEN YOU'RE READY FOR REAL DATA (fetch_real_data.py)
------------------------------------------------------
Run this ONCE on your own laptop, with internet, whenever convenient:

    pip install yfinance
    python fetch_real_data.py

It saves real NSE data into this same stock_data/ folder, same filenames,
same column structure. Every notebook cell you've already written keeps
working unchanged — you're just pointing at real numbers instead of sample
ones.
