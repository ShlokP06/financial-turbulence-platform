import pandas as pd
import pytest
from turballoc.ingest.market import to_returns
from turballoc.ingest.store import FeatureStore

def test_to_returns_log_shape(sample_prices):
    rets = to_returns(sample_prices, kind = "log")
    assert rets.shape[0] == sample_prices.shape[0] - 1
    assert list(rets.columns) == list(sample_prices.columns)

def test_to_returns_simple_matches_pct(sample_prices):
    rets = to_returns(sample_prices, kind = "simple")
    expected = sample_prices.pct_change().iloc[1:]
    pd.testing.assert_frame_equal(rets, expected)

def test_to_returns_invalid_kind(sample_prices):
    with pytest.raises(ValueError):
        to_returns(sample_prices, kind="bogus")

def test_feature_store_roundtrip(tmp_path, sample_prices):
    store = FeatureStore(tmp_path/"f.duckdb")
    store.write("prices", sample_prices)
    assert "prices" in store.list_tables()
    out = store.read("prices")
    pd.testing.assert_frame_equal(out, sample_prices, check_freq = False)
