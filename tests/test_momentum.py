"""Tests for the time-series momentum signals and tilts."""
import numpy as np
import pandas as pd
import pytest

from turballoc.allocation.momentum import (
    momentum_tilt,
    momentum_trend_filter,
    risk_adjusted_momentum,
    trailing_momentum,
)
from turballoc.allocation.strategy import CASH, turbulence_managed_weights


def _trending_returns(n=300, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-01", periods=n)
    up = rng.normal(0.0008, 0.01, n)      # positive drift
    down = rng.normal(-0.0008, 0.01, n)   # negative drift
    flat = rng.normal(0.0, 0.01, n)
    return pd.DataFrame({"UP": up, "DOWN": down, "FLAT": flat}, index=idx)


def test_trailing_momentum_sign_tracks_trend():
    m = trailing_momentum(_trending_returns())
    assert m["UP"] > 0 > m["DOWN"]


def test_trailing_momentum_skip_excludes_recent():
    r = _trending_returns()
    full = trailing_momentum(r, lookback=252, skip=0)
    skipped = trailing_momentum(r, lookback=252, skip=21)
    assert not np.isclose(full["UP"], skipped["UP"])  # the skipped month changes the value


def test_risk_adjusted_momentum_penalizes_volatility():
    idx = pd.bdate_range("2015-01-01", periods=300)
    # identical drift, controlled volatility (alternating noise cancels in the trend sum)
    sign = np.where(np.arange(300) % 2 == 0, 1.0, -1.0)
    r = pd.DataFrame({"LOVOL": 0.0006 + 0.001 * sign, "HIVOL": 0.0006 + 0.02 * sign}, index=idx)
    s = risk_adjusted_momentum(r)
    assert s["LOVOL"] > s["HIVOL"]  # same trend, lower vol -> larger risk-adjusted score


def test_momentum_tilt_overweights_high_score():
    base = pd.Series([0.25, 0.25, 0.25, 0.25], index=list("ABCD"))
    scores = pd.Series([2.0, 1.0, -1.0, -2.0], index=list("ABCD"))
    w = momentum_tilt(base, scores)
    assert w.sum() == pytest.approx(1.0)
    assert (w >= 0).all()
    assert w["A"] > base["A"] and w["D"] < base["D"]


def test_trend_filter_drops_downtrending_assets():
    base = pd.Series([0.5, 0.5], index=["UP", "DOWN"])
    raw = pd.Series([0.2, -0.1], index=["UP", "DOWN"])
    w = momentum_trend_filter(base, raw)
    assert w["DOWN"] == pytest.approx(0.0)
    assert w["UP"] == pytest.approx(1.0)
    # all-down -> fall back to the base rather than divide by zero
    fallback = momentum_trend_filter(base, pd.Series([-0.2, -0.1], index=["UP", "DOWN"]))
    assert fallback.sum() == pytest.approx(1.0)


@pytest.mark.parametrize("mode", ["continuous", "sign"])
def test_managed_weights_with_momentum_are_valid(mode):
    rng = np.random.default_rng(2)
    idx = pd.bdate_range("2015-01-01", periods=400)
    cols = ["AGG", "TLT", "LQD", "SPY", "EEM", "GLD"]
    rets = pd.DataFrame(rng.normal(0.0004, 0.01, size=(400, len(cols))), index=idx, columns=cols)
    turb = pd.Series(np.abs(rng.standard_normal(400)).cumsum() % 5 + 1, index=idx)
    w = turbulence_managed_weights(rets, turb, momentum=mode)
    assert w.sum() == pytest.approx(1.0)
    assert (w >= -1e-9).all()
    assert CASH in w.index
