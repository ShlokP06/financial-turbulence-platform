import pandas as pd
from turballoc.ingest.store import FeatureStore
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def build_risk_features(store = None, vol_window = 21):
    store = store or FeatureStore()
    returns = store.read("returns")
    feats = pd.DataFrame(index = returns.index)
    feats["mkt_return"] = returns.mean(axis = 1)
    feats["cross_section_vol"] = returns.std(axis = 1)
    feats["realized_vol"] = returns.mean(axis = 1).rolling(vol_window).std()
    tables = store.list_tables()
    if "turbulence" in tables:
        feats["turbulence"] = store.read('turbulence')["turbulence"]
    if "credit" in tables:
        feats["credit_stress"] = store.read("credit")["credit_stress"].reindex(feats.index)
    if "sentiment" in tables:
        feats["sentiment"] = store.read("sentiment")["sentiment"].reindex(feats.index)
    
    feats = feats.dropna()
    logger.info("Build risk feature matrix: %d rows x %d cols", feats.shape[0], feats.shape[1])
    return feats

