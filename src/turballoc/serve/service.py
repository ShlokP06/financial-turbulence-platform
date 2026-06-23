import numpy as np
from turballoc.allocation.black_litterman import black_litterman, implied_equilibrium_returns, mean_variance_weights
import pandas as pd

def latest_turbulence(store):
    df = store.read("turbulence").dropna(subset = ["turbulence"])
    if df.empty:
        return None
    row = df.iloc[-1]
    return {
        "date": df.index[-1].date().isoformat(),
        "turbulence": float(row["turbulence"]),
        "regime": str(row["regime"])
    }

def compute_weights(store, lookback = 252, risk_aversion = 2.5):
    returns = store.read("returns").dropna(how = "any")
    recent = returns.iloc[-lookback:]
    cov = recent.cov() * 252
    n = cov.shape[1]
    w_mkt = np.ones(n) / n
    w_mkt = pd.Series(w_mkt, index = cov.columns)
    pi = implied_equilibrium_returns(cov, w_mkt, risk_av = risk_aversion)
    mu = black_litterman(cov, pi, np.zeros((0,n)), np.zeros(0))
    return mean_variance_weights(mu, cov, risk_av = risk_aversion)

