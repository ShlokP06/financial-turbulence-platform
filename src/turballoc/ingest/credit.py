import datetime as dt
import pandas as pd
from turballoc.ingest.market import fetch_prices, to_returns
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def fetch_credit(start = "2010-01-01", end = None, prices = None):
    # Reuse already-fetched prices if they cover HYG/LQD; the main ingest pulls
    # both in its default basket, so a second yfinance download here is redundant
    # (and back-to-back calls get rate-limited).
    if prices is not None and {"HYG", "LQD"}.issubset(prices.columns):
        prices = prices[["HYG", "LQD"]]
    else:
        prices = fetch_prices(("HYG", "LQD"), start, end)
    rets = to_returns(prices, kind = "log")
    out = pd.DataFrame(index = rets.index)
    out.index.name = 'date'
    out["credit_stress"] = rets["LQD"] - rets["HYG"]
    out["hyg_lqd_ratio"] = (prices["HYG"] / prices["LQD"]).reindex(out.index)
    logger.info("Built credit proxy")
    return out

