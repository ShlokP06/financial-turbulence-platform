"""Seed the feature store with synthetic data so the API and dashboard work without a full ETL run.

Writes `returns` and `turbulence` tables into the default DuckDB feature store (the same one
`turballoc.serve.app` reads). Run once for local dev / demos:

    python scripts/seed_demo.py
"""

import numpy as np
import pandas as pd

from turballoc.ingest.store import FeatureStore
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

TICKERS = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "LQD", "HYG", "GLD", "DBC"]
WINDOW = 120  # trailing window for the Mahalanobis estimate


def make_returns(n: int = 504, seed: int = 42) -> pd.DataFrame:
    """Synthetic daily returns with a few correlated stress windows."""
    rng = np.random.default_rng(seed)
    # Index named "date" so FeatureStore persists/restores it (its round-trip convention).
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n, name="date")
    rets = rng.normal(0.0004, 0.009, size=(n, len(TICKERS)))
    # Inject elevated, correlated volatility to create visible turbulent regimes.
    for start, length in [(120, 25), (300, 18), (440, 30)]:
        rets[start : start + length] += rng.normal(-0.002, 0.03, size=(length, 1))
    return pd.DataFrame(rets, index=idx, columns=TICKERS)


def make_turbulence(returns: pd.DataFrame) -> pd.DataFrame:
    """Mahalanobis distance vs a trailing mean/cov (Kritzman-Li), with regime labels."""
    arr = returns.to_numpy()
    scores = np.full(len(returns), np.nan)
    for i in range(WINDOW, len(returns)):
        hist = arr[i - WINDOW : i]
        d = arr[i] - hist.mean(axis=0)
        cov = np.cov(hist, rowvar=False)
        try:
            scores[i] = float(d @ np.linalg.solve(cov, d))
        except np.linalg.LinAlgError:
            scores[i] = np.nan

    s = pd.Series(scores, index=returns.index, name="turbulence")
    valid = s.dropna()
    q50, q80, q95 = valid.quantile([0.5, 0.8, 0.95])

    def label(x: float):
        if np.isnan(x):
            return None
        if x < q50:
            return "calm"
        if x < q80:
            return "normal"
        if x < q95:
            return "elevated"
        return "turbulent"

    return pd.DataFrame({"turbulence": s, "regime": s.map(label)})


def main() -> None:
    store = FeatureStore()
    returns = make_returns()
    turbulence = make_turbulence(returns)
    store.write("returns", returns)
    store.write("turbulence", turbulence)
    logger.info("Seeded returns %s and turbulence %s", returns.shape, turbulence.shape)


if __name__ == "__main__":
    main()
