import numpy as np
import pandas as pd
import pytest
from turballoc.clustering.risk_profiles import RiskClusterer

def _two_blob_features(seed = 0):
    rng = np.random.default_rng(seed)
    calm = rng.normal(0.0, 0.5, size=(100, 3))
    crisis = rng.normal(8.0, 0.5, size=(100, 3))
    X = np.vstack([calm, crisis])
    idx = pd.bdate_range("2019-01-01", periods=200, name="date")
    return pd.DataFrame(X, index=idx, columns=["vol", "turbulence", "credit"])

def test_kmeans_recovers_two_blobs():
    feats = _two_blob_features()
    labels = RiskClusterer(n_clusters=2, method="kmeans", seed=0).fit(feats).predict(feats)
    assert labels.iloc[:100].nunique() == 1
    assert labels.iloc[100:].nunique() == 1
    assert labels.iloc[0] != labels.iloc[-1]

def test_predict_before_fit_raises():
    with pytest.raises(RuntimeError):
        RiskClusterer(n_clusters=2).predict(_two_blob_features())

def test_profiles_shape():
    feats = _two_blob_features()
    prof = RiskClusterer(n_clusters=2, seed=0).fit(feats).profiles(feats)
    assert prof.shape == (2, feats.shape[1])
    assert list(prof.columns) == list(feats.columns)

def test_invalid_method_raises():
    with pytest.raises(ValueError):
        RiskClusterer(n_clusters=2, method="dbscan").fit(_two_blob_features())
