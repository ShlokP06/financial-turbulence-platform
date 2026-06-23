import numpy as np
import pandas as pd
import pytest
from turballoc.allocation.bayesian import optimize_risk_av
from turballoc.allocation.black_litterman import (
    black_litterman,
    implied_equilibrium_returns,
    mean_variance_weights,
)

def _cov():
    assets = ["stocks", "bonds", "gold"]
    data = np.array([[0.040, 0.002, 0.001],
                     [0.002, 0.010, 0.000],
                     [0.001, 0.000, 0.020]])
    return pd.DataFrame(data, index=assets, columns=assets)

def test_no_views_returns_prior():
    cov = _cov()
    w_mkt = pd.Series([0.6, 0.3, 0.1], index=cov.index)
    pi = implied_equilibrium_returns(cov, w_mkt)
    # An empty view set must leave the posterior equal to the prior.
    post = black_litterman(cov, pi, np.zeros((0, 3)), np.zeros(0))
    np.testing.assert_allclose(post.to_numpy(), pi.to_numpy(), atol=1e-10)

def test_bullish_view_lifts_asset():
    cov = _cov()
    w_mkt = pd.Series([0.6, 0.3, 0.1], index=cov.index)
    pi = implied_equilibrium_returns(cov, w_mkt)
    # View: stocks return 15% (absolute), well above equilibrium.
    P, Q = [[1.0, 0.0, 0.0]], [0.15]
    post = black_litterman(cov, pi, P, Q)
    assert post["stocks"] > pi["stocks"]

def test_weights_sum_to_one_long_only():
    cov = _cov()
    mu = pd.Series([0.08, 0.02, -0.01], index=cov.index)
    w = mean_variance_weights(mu, cov, long_only=True)
    assert w.sum() == pytest.approx(1.0)
    assert (w >= 0).all()

def test_bayesian_opt_recovers_optimum():
    # Concave objective peaking at delta = 4; optimizer should land close.
    best_delta, best_score = optimize_risk_av(
        lambda d: -((d - 4.0) ** 2), bounds=(0.5, 10.0), n_calls=20, seed=0
    )
    assert abs(best_delta - 4.0) < 0.5
    assert best_score > -0.25
