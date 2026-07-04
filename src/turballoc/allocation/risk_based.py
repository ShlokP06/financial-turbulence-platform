"""Risk-based portfolio construction.

These allocators ignore expected returns entirely — the noisiest, hardest-to-estimate input
in mean-variance optimization — and build weights purely from the covariance. That removes the
"error maximization" instability of ``Sigma^-1 @ mu`` while still producing well-diversified,
low-turnover portfolios.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

DEFAULT_CAP = 0.35


def _apply_cap(weights: pd.Series, cap: float) -> pd.Series:
    """Clip weights to ``cap`` and redistribute the excess proportionally, then renormalize."""
    w = weights.clip(lower=0.0)
    for _ in range(50):
        over = w > cap
        if not over.any():
            break
        excess = float((w[over] - cap).sum())
        w[over] = cap
        under = ~over
        if w[under].sum() <= 0:
            break
        w[under] = w[under] + excess * w[under] / w[under].sum()
    total = w.sum()
    return w / total if total > 0 else w


def inverse_vol_weights(cov: pd.DataFrame) -> pd.Series:
    """Weights inversely proportional to each asset's volatility ("naive risk parity").

    Args:
        cov: Asset covariance matrix.

    Returns:
        Long-only weights summing to 1.
    """
    vol = np.sqrt(np.diag(cov.to_numpy()))
    inv = np.where(vol > 0, 1.0 / vol, 0.0)
    return pd.Series(inv / inv.sum(), index=cov.columns)


def risk_parity_weights(
    cov: pd.DataFrame, cap: float = DEFAULT_CAP, iters: int = 500, tol: float = 1e-10
) -> pd.Series:
    """Equal-risk-contribution (risk parity) weights via a multiplicative fixed point.

    Each asset is sized so it contributes an equal share of total portfolio risk.

    Args:
        cov: Asset covariance matrix.
        cap: Maximum weight per asset (excess is redistributed).
        iters: Maximum fixed-point iterations.
        tol: Convergence tolerance on the max weight change.

    Returns:
        Long-only weights summing to 1.
    """
    sigma = cov.to_numpy()
    n = sigma.shape[0]
    w = 1.0 / np.sqrt(np.diag(sigma))
    w = w / w.sum()
    for _ in range(iters):
        marginal = sigma @ w
        rc = w * marginal
        w_new = w * (rc.sum() / n) / (rc + 1e-12)
        w_new = np.clip(w_new, 0.0, None)
        w_new = w_new / w_new.sum()
        if np.abs(w_new - w).max() < tol:
            w = w_new
            break
        w = w_new
    return _apply_cap(pd.Series(w, index=cov.columns), cap)


def min_variance_weights(cov: pd.DataFrame, cap: float = DEFAULT_CAP) -> pd.Series:
    """Long-only global minimum-variance weights with a per-asset cap.

    Solves ``min w' Sigma w`` s.t. ``sum(w) = 1`` and ``0 <= w <= cap`` via SLSQP.

    Args:
        cov: Asset covariance matrix.
        cap: Maximum weight per asset.

    Returns:
        Long-only weights summing to 1.
    """
    sigma = cov.to_numpy()
    n = sigma.shape[0]
    result = minimize(
        lambda x: float(x @ sigma @ x),
        np.ones(n) / n,
        method="SLSQP",
        bounds=[(0.0, cap)] * n,
        constraints=({"type": "eq", "fun": lambda x: x.sum() - 1.0},),
        options={"maxiter": 200, "ftol": 1e-10},
    )
    w = np.clip(result.x, 0.0, None)
    total = w.sum()
    w = w / total if total > 0 else np.ones(n) / n
    return pd.Series(w, index=cov.columns)
