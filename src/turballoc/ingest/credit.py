import datetime as dt
import pandas as pd
from turballoc.ingest.market import fetch_prices, to_returns
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def fetch_credit(start = "2010-01-01", end = None):
    prices = fetch_prices(("HYG", "LQD"), start, end)
    rets = to_returns(prices, kind = "log")
    out = pd.DataFrame(index = rets.index)
    out.index.name = 'date'
    out["credit_stress"] = rets["LQD"] - rets["HYG"]
    out["hyg_lqd_ratio"] = (prices["HYG"] / prices["LQD"]).reindex(out.index)
    logger.info("Built credit proxy")
    return out

