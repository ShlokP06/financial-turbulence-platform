import numpy as np
import pandas as pd
from turballoc.explain.shap_explainer import explain_model, feature_importance, simple_counterfactual


def _data(n=80, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {"a": rng.normal(size=n), "b": rng.normal(size=n), "c": rng.normal(size=n)}
    )


def _predict(X):
    # a dominates, b is minor, c is irrelevant
    X = np.asarray(X, dtype=float)
    return 3.0 * X[:, 0] + 0.5 * X[:, 1]


def test_feature_importance_ranks_dominant_feature_first():
    df = _data()
    shap_df = explain_model(_predict, df.iloc[:30], df.iloc[30:40], nsamples=100)
    imp = feature_importance(shap_df)
    assert imp.index[0] == "a"
    assert imp["a"] > imp["c"]


def test_shap_shape_matches_instances():
    df = _data()
    inst = df.iloc[30:40]
    shap_df = explain_model(_predict, df.iloc[:30], inst, nsamples=100)
    assert shap_df.shape == inst.shape
    assert list(shap_df.columns) == list(inst.columns)


def test_counterfactual_monotonic_in_dominant_feature():
    df = _data()
    cf = simple_counterfactual(_predict, df.iloc[0], "a", [-2.0, -1.0, 0.0, 1.0, 2.0])
    preds = cf["prediction"].to_numpy()
    assert np.all(np.diff(preds) > 0)
