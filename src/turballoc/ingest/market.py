import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

defaults = ("SPY","EFA","EEM","AGG","TLT","LQD","HYG","GLD","DBC","VNQ")

def fetch_prices(tickers = defaults, start = "2010-01-01", end = None):
    raw = yf.download(list(tickers), start = str(start),
                      end = str(end) if end is not None else None,
                      auto_adjust=True, progress=False)
    if raw is None or raw.empty:
        raise ValueError("yfinance returned no data")
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"].copy()
    else:
        prices = raw[["Close"]].copy()
        prices.columns = [tickers[0]]
    prices = prices.dropna(how='all').sort_index()
    prices.index = pd.to_datetime(prices.index)
    prices.index.name = "date"
    missing = [t for t in tickers if t not in prices.columns]
    if missing:
        logger.warning("No data for tickers: %s", missing)
    logger.info("Fetched %d rows x %d tickers", prices.shape[0], prices.shape[1])
    return prices

def to_returns(prices, kind = "log"):
    if kind == 'log':
        rets = np.log(prices/prices.shift(1))
    elif kind == "simple":
        rets = prices.pct_change()
    else:
        raise ValueError(f"kind must be 'log' or 'simple'. got {kind!r}")
    return rets.iloc[1:]

