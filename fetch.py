"""
fetch.py

Downloads daily OHLCV data for all tickers defined in config.py
and saves each to data/<TICKER>.csv.

Run once to populate the data/ folder:
    python fetch.py
"""

import yfinance as yf
from config import TICKERS, START_DATE, END_DATE

for ticker in TICKERS:
    df = yf.download(ticker, start=START_DATE, end=END_DATE, auto_adjust=True)
    filepath = f'data/{ticker}.csv'
    df.to_csv(filepath)
    print(f"Saved {filepath} — shape: {df.shape}")
