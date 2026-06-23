import numpy as np
import pandas as pd
import pytest
from turballoc.backtest.engine import walk_forward_backtest
from turballoc.backtest.metrics import max_drawdown, sharpe_ratio

def _returns(n = 600, k = 3, seed = 0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-01", periods = n, name = "date")
    data = rng.normal(0.0005, 0.01, size = (n, k))
    return pd.DataFrame(data, index = idx, columns = ["a", "b", "c"])

def test_max_drawdown_known():
    r = pd.Series([0.1, -0.5, 0.2])
    assert max_drawdown(r) == pytest.approx(-0.5)

def test_sharpe_when_flat():
    assert sharpe_ratio(pd.Series([0.0] * 10)) == 0.0

def test_equal_weight_runs():
    rets = _returns()
    def eq(past):
        return pd.Series(1.0 / past.shape[1], index = past.columns)
    port, weights, stats = walk_forward_backtest(rets, eq, lookback = 100,
                                                 rebalance = 20, cost = 0.0)
    assert len(port) == len(rets) - 100
    assert {"sharpe", "max_drawdown", "ann_return"} <= set(stats)

def test_no_lookahead():
    rets = _returns(n = 300)
    seen = {"max_len": 0}
    def spy(past):
        seen["max_len"] = max(seen["max_len"], len(past))
        return pd.Series(1.0 / past.shape[1], index = past.columns)
    walk_forward_backtest(rets, spy, lookback = 100, rebalance = 20, cost = 0.0)
    assert seen["max_len"] <= len(rets) - 1

def test_costs_reduce_return():
    rets = _returns()
    flip = {"i": 0}
    def churn(past):
        flip["i"] += 1
        w = [1.0, 0.0, 0.0] if flip["i"] % 2 else [0.0, 0.0, 1.0]
        return pd.Series(w, index = past.columns)
    free, _, _ = walk_forward_backtest(rets, churn, lookback = 100, rebalance = 20, cost = 0.0)
    costly, _, _ = walk_forward_backtest(rets, churn, lookback = 100, rebalance = 20, cost = 0.01)
    assert costly.sum() < free.sum()
