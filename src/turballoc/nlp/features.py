import pandas as pd
from turballoc.ingest.store import FeatureStore
from turballoc.logging_utils import get_logger
from turballoc.nlp import sentiment

logger = get_logger(__name__)

def daily_sentiment(frame, text_col = "title"):
    out_cols = ["sentiment", "count"]
    if frame.empty:
        idx = pd.DatetimeIndex([], name="date")
        return pd.DataFrame({c: pd.Series(dtype="float64") for c in out_cols}, index = idx)
    texts = frame[text_col].astype(str).tolist()
    scored = sentiment.score_texts(texts)
    scored.index = pd.to_datetime(frame.index)
    daily = scored.groupby(scored.index.normalize())["sentiment"].agg(["mean", "count"])
    daily.columns = out_cols
    daily.index.name = "date"
    return daily.sort_index()

def build_sentiment_feature(frame, text_col = "title", store = None):
    "Build the daily sentiment feature"
    daily = daily_sentiment(frame, text_col=text_col)
    store = store or FeatureStore()
    store.write("sentiment", daily)
    logger.info("Wrote sentiment feature: %d days", len(daily))
    return daily
