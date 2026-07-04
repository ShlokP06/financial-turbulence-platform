"""Covariance estimation for portfolio construction.

A raw sample covariance over a short window is noisy, and inverting it (as mean-variance
optimization does) amplifies that noise into unstable, extreme weights — the classic
"error maximization" problem (Michaud, 1989). Ledoit-Wolf shrinkage pulls the sample
covariance toward a well-conditioned target, which stabilizes every downstream optimizer.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from sklearn.covariance import LedoitWolf

    _HAVE_SKLEARN = True
except Exception:  # pragma: no cover - sklearn is a declared dependency
    _HAVE_SKLEARN = False

TRADING_DAYS = 252


def shrunk_covariance(
    returns: pd.DataFrame, annualize: bool = True, periods: int = TRADING_DAYS
) -> pd.DataFrame:
    """Estimate a Ledoit-Wolf shrunk covariance from a window of periodic returns.

    Args:
        returns: Window of periodic (e.g. daily) asset returns, assets in columns.
        annualize: If True, scale the (per-period) covariance by ``periods``.
        periods: Periods per year used for annualization.

    Returns:
        A ``(n_assets, n_assets)`` covariance ``DataFrame`` indexed by asset.
    """
    X = returns.to_numpy()
    if _HAVE_SKLEARN and X.shape[0] > X.shape[1] + 2:
        cov = LedoitWolf().fit(X).covariance_
    else:  # fallback: sample covariance shrunk halfway toward its diagonal
        sample = np.cov(X, rowvar=False)
        cov = 0.5 * sample + 0.5 * np.diag(np.diag(sample))
    if annualize:
        cov = cov * periods
    return pd.DataFrame(cov, index=returns.columns, columns=returns.columns)
