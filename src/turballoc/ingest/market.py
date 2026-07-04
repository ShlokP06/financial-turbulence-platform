import time
import numpy as np
import pandas as pd
import yfinance as yf
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

defaults = ("SPY","EFA","EEM","AGG","TLT","LQD","HYG","GLD","DBC","VNQ")
# Expanded universe: adds distinct, low-correlation sleeves that raise effective breadth
# (T-bills, TIPS, oil, EM bonds) — all with full history from 2010. DBMF (managed futures)
# is deliberately excluded from the default expansion because it only launched in 2019 and
# would truncate the backtest; build it on a shorter window separately if desired.
expanded = defaults + ("BIL","TIP","USO","EMB")

def _download_close(ticker, start, end):
    "Single-ticker adjusted-close series, or None if Yahoo returned nothing."
    raw = yf.download(ticker, start = str(start),
                      end = str(end) if end is not None else None,
                      auto_adjust=True, progress=False, threads=False)
    if raw is None or raw.empty or "Close" not in raw:
        return None
    close = raw["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.dropna()

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
    # Yahoo throttling silently returns all-NaN (or sparse) columns instead of erroring.
    # The concurrent multi-ticker download tends to drop a few under load, so backfill
    # those one at a time (gentler, sequential) before giving up. These basket ETFs all
    # predate the 2010 start, so real coverage is ~1.0.
    coverage = prices.notna().mean()
    bad = [t for t in tickers if coverage.get(t, 0.0) < 0.5]
    for t in list(bad):
        for attempt in range(3):
            time.sleep(1.0)
            close = _download_close(t, start, end)
            if close is not None and len(close) >= 0.5 * len(prices):
                prices[t] = close.reindex(prices.index)
                bad.remove(t)
                break
    if bad:
        raise ValueError(f"yfinance returned little/no data for {bad} (likely rate-limited); retry later")
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

