import numpy as np
import pandas as pd
from turballoc.allocation.covariance import shrunk_covariance
from turballoc.allocation.momentum import (
    momentum_tilt,
    momentum_trend_filter,
    risk_adjusted_momentum,
    trailing_momentum,
)
from turballoc.allocation.risk_based import min_variance_weights

# Defaults for the turbulence-managed risk-parity strategy.
CASH = "CASH"
TURB_WINDOW = 756       # ~3y rolling window for the turbulence percentile
TURB_THRESHOLD = 0.70   # de-risking starts above this turbulence percentile
TURB_FLOOR = 0.30       # minimum gross exposure at peak turbulence
TARGET_VOL = 0.07       # annualized volatility target for the base book
WEIGHT_CAP = 0.35

def signal_exposure(
    signal_history: pd.Series,
    window: int = TURB_WINDOW,
    threshold: float = TURB_THRESHOLD,
    floor: float = TURB_FLOOR,
) -> float:
    """Gross-exposure scalar in ``[floor, 1]`` from where a risk signal sits in its recent range.

    Below ``threshold`` (a percentile) the book is fully invested; above it, exposure ramps
    linearly down to ``floor`` at the most extreme reading. A rolling percentile (not an
    expanding one) keeps the signal stationary. The signal may be contemporaneous turbulence or
    a forecast exceedance probability. ``signal_history`` must contain only data up to the as-of
    date (the caller slices it), keeping the backtest leak-free.

    Args:
        signal_history: Risk signal series up to and including the as-of date.
        window: Rolling window (observations) for the percentile.
        threshold: Percentile above which de-risking begins.
        floor: Minimum gross exposure.

    Returns:
        A scalar in ``[floor, 1.0]``; the remainder is held in cash.
    """
    s = signal_history.dropna()
    if s.empty:
        return 1.0
    recent = s.iloc[-window:]
    pct = float((recent <= recent.iloc[-1]).mean())
    if pct <= threshold:
        return 1.0
    ramp = (pct - threshold) / (1.0 - threshold)
    return float(1.0 - (1.0 - floor) * ramp)


def turbulence_exposure(
    turbulence_history: pd.Series,
    window: int = TURB_WINDOW,
    threshold: float = TURB_THRESHOLD,
    floor: float = TURB_FLOOR,
) -> float:
    """Exposure scalar driven by contemporaneous turbulence (see :func:`signal_exposure`).

    Turbulence is used the way Kritzman-Li intended — as a risk/exposure signal, not a
    cross-sectional return view.
    """
    return signal_exposure(turbulence_history, window=window, threshold=threshold, floor=floor)


def vol_target_scale(weights: pd.Series, cov_annual: pd.DataFrame, target_vol: float) -> float:
    """Exposure scalar that targets a fixed annualized volatility, capped at 1 (no leverage).

    Args:
        weights: Base-portfolio weights (summing to 1).
        cov_annual: Annualized covariance of the assets.
        target_vol: Desired annualized portfolio volatility.

    Returns:
        ``min(1, target_vol / realized_vol)``.
    """
    w = weights.reindex(cov_annual.columns).fillna(0.0).to_numpy()
    port_vol = float(np.sqrt(max(w @ cov_annual.to_numpy() @ w, 1e-12)))
    return float(min(1.0, target_vol / port_vol))


def turbulence_managed_weights(
    returns_window: pd.DataFrame,
    turbulence_history: pd.Series,
    *,
    overlay_history: pd.Series | None = None,
    momentum: str | None = None,
    cap: float = WEIGHT_CAP,
    target_vol: float = TARGET_VOL,
    turb_window: int = TURB_WINDOW,
    threshold: float = TURB_THRESHOLD,
    floor: float = TURB_FLOOR,
) -> pd.Series:
    """Turbulence-managed minimum-variance strategy weights (assets + ``CASH``).

    Three independently-motivated layers: (1) a Ledoit-Wolf-shrunk minimum-variance base
    (low-volatility tilt, no expected-return estimation), (2) volatility targeting, and
    (3) a turbulence-driven exposure overlay that scales the whole book toward cash when
    turbulence spikes. The de-risked remainder is reported as a ``CASH`` weight so the caller
    can credit it a risk-free return.

    Args:
        returns_window: Trailing window of periodic asset returns (assets in columns).
        turbulence_history: Turbulence series up to the as-of date (default overlay signal).
        overlay_history: Optional alternative overlay signal up to the as-of date (e.g. a
            forecast exceedance probability); when given it drives the exposure overlay instead
            of contemporaneous turbulence.
        momentum: Optional time-series-momentum tilt on the base: ``"continuous"`` (risk-adjusted
            trend tilt) or ``"sign"`` (drop downtrending assets); ``None`` disables it.
        cap: Per-asset weight cap for the minimum-variance base.
        target_vol: Annualized volatility target.
        turb_window: Rolling window for the turbulence percentile.
        threshold: Turbulence percentile above which de-risking begins.
        floor: Minimum gross exposure at peak turbulence.

    Returns:
        Weights over the assets plus a ``CASH`` entry, summing to 1.
    """
    cov = shrunk_covariance(returns_window, annualize=True)
    weights = min_variance_weights(cov, cap=cap)
    if momentum == "continuous":
        weights = momentum_tilt(weights, risk_adjusted_momentum(returns_window))
    elif momentum == "sign":
        weights = momentum_trend_filter(weights, trailing_momentum(returns_window))
    exposure = vol_target_scale(weights, cov, target_vol)
    overlay = overlay_history if overlay_history is not None else turbulence_history
    exposure *= signal_exposure(overlay, window=turb_window, threshold=threshold, floor=floor)
    weights = weights * exposure
    weights[CASH] = 1.0 - exposure
    return weights
