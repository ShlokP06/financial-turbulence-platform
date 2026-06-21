import numpy as np
import pandas as pd
from turballoc.ingest.store import FeatureStore
from turballoc.signals.regime import Regime, classify_regime
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def turbulence_index(returns, window = 252, min_periods = 126):
    returns = returns.dropna(how="any")
    values = returns.to_numpy()
    n = len(returns)
    out = np.full(n, np.nan)
    for t in range(n):
        past = values[max(0, t - window): t]
        if len(past) < min_periods:
            continue
        mu =past.mean(axis=0)
        cov_inv = np.linalg.pinv(np.cov(past, rowvar = False))
        diff = values[t] - mu
        out[t] = float(diff @ cov_inv @ diff)
    turb = pd.Series(out, index = returns.index, name = "turbulence")
    logger.info("Computed turbulence: %d/%d valid days", int(np.isfinite(out).sum()), n)
    return turb

def build_turbulence_feature(window = 252, store = None):
    store = store or FeatureStore()
    returns = store.read("returns")
    turb = turbulence_index(returns, window = window)
    regime = classify_regime(turb, window = window)
    out = pd.DataFrame({"turbulence": turb})
    labels = {r: r.value for r in Regime}
    out["regime"] = regime.map(labels)
    out.index.name = "date"
    store.write("turbulence", out)
    logger.info(f"Wrote turbulence feature for {len(out)} days")
    return out
