import numpy as np
import pandas as pd
import pytest

from turballoc.explain.news_explainer import asset_drivers


class _FakeStore:
    """Minimal store stub exposing read(table) -> DataFrame, like FeatureStore."""

    def __init__(self, returns):
        self._returns = returns

    def read(self, table):
        assert table == "returns"
        return self._returns


def _returns(n=150, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    data = rng.normal(scale=0.01, size=(n, 3))
    return pd.DataFrame(data, index=idx, columns=["AAA", "BBB", "CCC"])


def test_asset_drivers_ranks_largest_standardized_move_first():
    rets = _returns()
    target = rets.index[-1]
    # Inject a large idiosyncratic shock into BBB on the target day.
    rets.loc[target, "BBB"] = 0.20
    drivers = asset_drivers(_FakeStore(rets), target, top_k=3)
    assert drivers[0]["asset"] == "BBB"
    assert abs(drivers[0]["z"]) > abs(drivers[-1]["z"])
    assert set(drivers[0]) == {"asset", "ret", "z"}


def test_asset_drivers_respects_top_k():
    rets = _returns()
    drivers = asset_drivers(_FakeStore(rets), rets.index[-1], top_k=2)
    assert len(drivers) == 2


def test_asset_drivers_raises_for_date_without_returns():
    rets = _returns()
    with pytest.raises(ValueError):
        asset_drivers(_FakeStore(rets), pd.Timestamp("1990-01-01"))
