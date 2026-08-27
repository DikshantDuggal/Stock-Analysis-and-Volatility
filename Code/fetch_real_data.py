"""
Run this ONCE, on your own laptop, whenever you have internet — takes about
a minute for all 18 stocks. It overwrites the sample CSVs in stock_data/
with real NSE data, same filenames, same columns. Nothing else in your
notebook needs to change afterward.

Usage:
    pip install yfinance
    python fetch_real_data.py
"""
import os
import yfinance as yf

SECTORS = {
    "IT":      ["TCS.NS", "INFY.NS", "WIPRO.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
    "Auto":    ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS"],
    "Pharma":  ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"],
    "FMCG":    ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS"],
    "Energy":  ["RELIANCE.NS", "ONGC.NS", "NTPC.NS"],
}
START_DATE, END_DATE = "2024-01-01", "2026-01-01"

os.makedirs("stock_data", exist_ok=True)

all_tickers = [t for tickers in SECTORS.values() for t in tickers]

for ticker in all_tickers:
    print(f"Fetching {ticker} ...")
    df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df.index.name = "Date"

    fname = ticker.replace("&", "AND").replace(".", "_") + ".csv"
    df.to_csv(f"stock_data/{fname}")

print("Done. stock_data/ now has real NSE prices instead of sample data.")
