import numpy as np
import pandas as pd
import pytest

@pytest.fixture
def sample_prices():
    idx = pd.bdate_range("2020-01-01", periods=10, name = "date")
    rng = np.random.default_rng(0)
    steps = rng.normal(0.0, 0.01, size=(10,3))
    prices = 100.0 * np.exp(np.cumsum(steps, axis=0))
    return pd.DataFrame(prices, index=idx, columns=["A", "B", "C"])

