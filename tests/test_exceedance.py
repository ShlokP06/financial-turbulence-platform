"""Tests for the forward-turbulence exceedance forecaster."""
import numpy as np
import pandas as pd
import pytest

from turballoc.allocation.strategy import CASH, signal_exposure, turbulence_managed_weights
from turballoc.forecast.exceedance import (
    build_exceedance_dataset,
    latest_exceedance_probability,
    walk_forward_probabilities,
)


class _Store:
    """Minimal in-memory store with enough history for the warm-up windows."""

    def __init__(self, n=1400, seed=0):
        rng = np.random.default_rng(seed)
        idx = pd.bdate_range("2014-01-01", periods=n, name="date")
        cols = ["AGG", "DBC", "EEM", "EFA", "GLD", "HYG", "LQD", "SPY", "TLT", "VNQ"]
        self._returns = pd.DataFrame(rng.normal(0.0004, 0.01, size=(n, len(cols))), index=idx, columns=cols)
        # autocorrelated, right-skewed turbulence so exceedance has signal
        base = np.abs(rng.standard_normal(n)).cumsum() % 5 + rng.gamma(2.0, 1.0, n)
        self._turb = pd.DataFrame({"turbulence": base, "regime": ["calm"] * n}, index=idx)
        self._credit = pd.DataFrame(
            {"credit_stress": rng.normal(0, 1, n), "hyg_lqd_ratio": rng.normal(1, 0.05, n)}, index=idx
        )

    def read(self, table):
        return {"returns": self._returns, "turbulence": self._turb, "credit": self._credit}[table]

    def list_tables(self):
        return ["returns", "turbulence", "credit"]


def test_exceedance_dataset_is_binary_and_clean():
    feats, y, cols = build_exceedance_dataset(_Store(), k=10)
    assert len(cols) == feats.shape[1]
    assert not feats.isna().any().any()
    assert set(np.unique(y.to_numpy())) <= {0.0, 1.0}
    assert 0.0 < float(y.mean()) < 1.0  # a non-degenerate base rate


def test_walk_forward_probabilities_are_leak_safe_and_in_unit_interval():
    feats, y, _ = build_exceedance_dataset(_Store(), k=10)
    prob = walk_forward_probabilities(feats, y, k=10, refit_every=21)
    assert prob.index.isin(feats.index).all()       # only scores in-sample dates
    assert ((prob >= 0.0) & (prob <= 1.0)).all()
    assert prob.index.min() > feats.index.min()      # warm-up before first score


def test_latest_probability_in_unit_interval():
    p = latest_exceedance_probability(_Store(), k=10)
    assert p is None or 0.0 <= p <= 1.0


def test_managed_weights_accept_forecast_overlay():
    store = _Store()
    rets = store.read("returns")
    feats, y, _ = build_exceedance_dataset(store, k=10)
    prob = walk_forward_probabilities(feats, y, k=10)
    # high latest probability -> de-risk into cash
    spike = prob.copy()
    spike.iloc[-1] = 1.0
    w = turbulence_managed_weights(rets.iloc[-300:], store.read("turbulence")["turbulence"],
                                   overlay_history=spike)
    assert w.sum() == pytest.approx(1.0)
    assert CASH in w.index


def test_signal_exposure_monotone():
    hist = pd.Series(np.linspace(0.0, 1.0, 500))
    assert signal_exposure(hist, threshold=0.7, floor=0.3) == pytest.approx(0.3)  # latest = max
    calm = pd.Series(list(np.linspace(0.0, 1.0, 499)) + [0.0])
    assert signal_exposure(calm, threshold=0.7, floor=0.3) == pytest.approx(1.0)
