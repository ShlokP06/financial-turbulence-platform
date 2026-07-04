"""Time-series (trend) momentum signals and tilts.

Time-series momentum — an asset's own past ~12-month trend predicting its next-period return —
is among the most replicated, out-of-sample-robust premia in asset pricing (Moskowitz, Ooi &
Pedersen 2012; Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following"). It is a
deterministic *signal*, not a fitted forecaster, which is exactly why it does not overfit the way
a learned return model does. Here it composes with the risk-based allocators as a tilt: it
over/under-weights the risk-balanced base by each asset's trend, which also gives the strategy a
principled way to re-risk into recoveries and shrink persistent downtrends.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MOM_LOOKBACK = 252      # ~12 months
MOM_SKIP = 21           # exclude the most recent ~1 month (avoids short-term reversal)
MOM_VOL_WINDOW = 60
TILT_STRENGTH = 0.5
TILT_MIN, TILT_MAX = 0.5, 1.5


def trailing_momentum(
    returns_window: pd.DataFrame, lookback: int = MOM_LOOKBACK, skip: int = MOM_SKIP
) -> pd.Series:
    """Cumulative trend return over the trailing ``lookback`` periods, excluding the last ``skip``.

    Assumes log returns (so a sum is a cumulative log return). Causal: uses only the window given.

    Args:
        returns_window: Trailing window of periodic log returns (assets in columns).
        lookback: Trend window length in periods.
        skip: Most-recent periods to exclude (short-term reversal guard).

    Returns:
        Per-asset cumulative trend return.
    """
    seg = returns_window.iloc[-lookback:]
    if skip > 0 and len(seg) > skip:
        seg = seg.iloc[:-skip]
    return seg.sum()


def risk_adjusted_momentum(
    returns_window: pd.DataFrame,
    lookback: int = MOM_LOOKBACK,
    skip: int = MOM_SKIP,
    vol_window: int = MOM_VOL_WINDOW,
) -> pd.Series:
    """Trend per unit of recent volatility (Moskowitz-Ooi-Pedersen scaling)."""
    mom = trailing_momentum(returns_window, lookback, skip)
    vol = returns_window.iloc[-vol_window:].std().replace(0.0, np.nan)
    return (mom / vol).fillna(0.0)


def momentum_tilt(
    base_weights: pd.Series,
    scores: pd.Series,
    strength: float = TILT_STRENGTH,
    lo: float = TILT_MIN,
    hi: float = TILT_MAX,
) -> pd.Series:
    """Continuous tilt: over/under-weight the base by a cross-sectionally standardized score.

    Args:
        base_weights: Risk-based base weights (summing to 1).
        scores: Per-asset momentum scores.
        strength: Tilt sensitivity (0 = no tilt).
        lo, hi: Bounds on the per-asset multiplier.

    Returns:
        Tilted long-only weights summing to 1.
    """
    s = scores.reindex(base_weights.index)
    z = (s - s.mean()) / (s.std() + 1e-12)
    mult = (1.0 + strength * z).clip(lo, hi).fillna(1.0)
    w = (base_weights * mult).clip(lower=0.0)
    total = w.sum()
    return w / total if total > 0 else base_weights


def momentum_trend_filter(
    base_weights: pd.Series, raw_momentum: pd.Series, downweight: float = 0.0
) -> pd.Series:
    """Sign filter: zero (or down-weight) assets in a downtrend, then renormalize.

    Args:
        base_weights: Risk-based base weights (summing to 1).
        raw_momentum: Per-asset trend return; non-positive values are de-emphasized.
        downweight: Factor applied to downtrending assets (0 = drop them entirely).

    Returns:
        Filtered long-only weights summing to 1 (falls back to the base if all trends are down).
    """
    factor = pd.Series(
        np.where(raw_momentum.reindex(base_weights.index).fillna(-1.0) > 0, 1.0, downweight),
        index=base_weights.index,
    )
    w = base_weights * factor
    total = w.sum()
    return w / total if total > 0 else base_weights
