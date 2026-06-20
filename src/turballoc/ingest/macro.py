import datetime as dt
import pandas as pd
from fredapi import Fred
from turballoc.config import settings
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)
default = {"DGS10": "treasury_10y", "DGS2": "treasury_2y", "T10Y2Y": "term_spread_10y2y",
           "VIXCLS": "vix", "BAMLH0A0HYM2": "hy_oas", "DTWEXBGS": "usd_broad_index",
           "DFF": "fed_funds_rate"}

def fetch_macro_series(series = None, start = "2010-01-01", end = None):
    if not settings.fred_api_key:
        raise ValueError("FRED_API_KEY is not set")
    series = series or default
    fred = Fred(api_key = settings.fred_api_key)
    columns = {}
    for series_id, name in series.items():
        s = fred.get_series(series_id, observation_start=str(start),
                            observation_end=str(end) if end is not None else None)
        columns[name] = s
        logger.info("fetched FRED series %s (%s): %d obs", series_id, name, len(s))
    frame = pd.DataFrame(columns)
    frame.index = pd.to_datetime(frame.index)
    frame.index.name = "date"
    frame = frame.sort_index().asfreq("B").ffill()
    return frame

