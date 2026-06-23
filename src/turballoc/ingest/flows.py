from turballoc.ingest.credit import fetch_credit
from turballoc.ingest.macro import fetch_macro_series
from turballoc.ingest.market import defaults, fetch_prices, to_returns
from turballoc.ingest.store import FeatureStore
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def build_structured_features(tickers = defaults, start = "2010-01-01",
                              end = None, include_macro = True):
    store = FeatureStore()
    prices = fetch_prices(tickers, start, end)
    returns = to_returns(prices, kind='log')
    store.write("prices", prices)
    store.write("returns", returns)
    credit = fetch_credit(start, end)
    store.write("credit", credit)
    if include_macro:
        macro = fetch_macro_series(start=start, end=end)
        store.write("macro", macro)

    logger.info("Structured Features build. Tables: %s", store.list_tables())

def main():
    build_structured_features()

if __name__ == "__main__":
    main()

