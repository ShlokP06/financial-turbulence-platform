import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from turballoc.serve.app import app, get_store


class FakeStore:
    """Stands in for FeatureStore so the API can be tested without DuckDB or ETL."""

    def __init__(self, returns, turbulence, credit=None):
        self._tables = {"returns": returns, "turbulence": turbulence}
        if credit is not None:
            self._tables["credit"] = credit

    def read(self, table):
        return self._tables[table]

    def list_tables(self):
        return list(self._tables)


def _data(n=300, k=4, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    cols = [f"A{i}" for i in range(k)]
    returns = pd.DataFrame(rng.normal(0.0005, 0.01, size=(n, k)), index=idx, columns=cols)
    turbulence = pd.DataFrame(
        {
            "turbulence": rng.gamma(2.0, 1.0, size=n),
            "regime": ["calm"] * (n - 1) + ["turbulent"],
        },
        index=idx,
    )
    return returns, turbulence


def _regime_data(n=900, seed=1):
    """Store shaped for the exceedance model: SPY/EEM returns, turbulence, and a credit table."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2016-01-01", periods=n, freq="B")
    cols = ["SPY", "EEM", "TLT", "GLD"]
    returns = pd.DataFrame(rng.normal(0.0004, 0.01, size=(n, len(cols))), index=idx, columns=cols)
    turbulence = pd.DataFrame(
        {"turbulence": np.abs(rng.gamma(2.0, 1.0, size=n)), "regime": ["normal"] * n},
        index=idx,
    )
    credit = pd.DataFrame(
        {
            "credit_stress": rng.normal(0.0, 1.0, size=n).cumsum() / 50.0,
            "hyg_lqd_ratio": 1.0 + rng.normal(0.0, 0.01, size=n).cumsum() / 50.0,
        },
        index=idx,
    )
    return returns, turbulence, credit


def _client(returns=None, turbulence=None, credit=None):
    if returns is None:
        returns, turbulence = _data()
    store = FakeStore(returns, turbulence, credit)
    app.dependency_overrides[get_store] = lambda: store
    return TestClient(app)


def test_health():
    client = _client()
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "returns" in body["tables"]


def test_turbulence_latest():
    client = _client()
    r = client.get("/turbulence/latest")
    assert r.status_code == 200
    body = r.json()
    assert body["regime"] == "turbulent"
    assert isinstance(body["turbulence"], float)


def test_weights_sum_to_one():
    client = _client()
    r = client.get("/weights", params={"target_vol": 0.05})
    assert r.status_code == 200
    body = r.json()
    w = body["weights"]
    assert abs(sum(w.values()) - 1.0) < 1e-6
    assert all(v >= 0 for v in w.values())
    assert body["target_vol"] == 0.05


def test_regime_risk_ok():
    returns, turbulence, credit = _regime_data()
    client = _client(returns, turbulence, credit)
    r = client.get("/regime/risk")
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["probability"] <= 1.0
    assert body["horizon_days"] == 10
    assert isinstance(body["as_of"], str) and body["as_of"]


def test_regime_risk_missing_credit_degrades():
    # No credit table (and no SPY/EEM columns) -> graceful 404, never a 500.
    client = _client()
    r = client.get("/regime/risk")
    assert r.status_code == 404


def test_latency_header_present():
    client = _client()
    r = client.get("/health")
    assert "X-Process-Time-ms" in r.headers
