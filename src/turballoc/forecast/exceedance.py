"""Forward-turbulence exceedance classifier.

Forecasting the turbulence *level* is a dead end: turbulence is highly autocorrelated, so a
level regressor is statistically indistinguishable from "predict the running mean", and a deep
LSTM-CNN is beaten by persistence at every actionable horizon. The learnable, leak-resistant,
and *useful* target is exceedance — "will turbulence cross a high trailing threshold within the
next ``k`` days?" A small regularized logistic regression on engineered features beats the
persistence baseline on out-of-sample AUC, and its probability is exactly the leading de-risk
trigger the allocation overlay consumes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

EXCEEDANCE_HORIZON = 10       # k: forecast window in trading days
EXCEEDANCE_QUANTILE = 0.90    # "high turbulence" = above this trailing quantile
THRESHOLD_WINDOW = 756        # ~3y trailing window for the causal threshold
MIN_THRESHOLD_OBS = 252
REGULARIZATION_C = 1.0


def build_exceedance_dataset(
    store,
    k: int = EXCEEDANCE_HORIZON,
    q: float = EXCEEDANCE_QUANTILE,
    thr_window: int = THRESHOLD_WINDOW,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Build causal engineered features and the forward-exceedance label.

    Every feature is known at time ``t`` (causal); the label ``y_t`` is 1 if turbulence exceeds
    its trailing ``q``-quantile (also known at ``t``) at any point in ``t+1..t+k``. The label is
    forward-looking by construction (that is what is being forecast) — callers must only ever
    train on rows whose label window has fully elapsed (see :func:`walk_forward_probabilities`).

    Args:
        store: Feature store exposing ``returns``, ``turbulence`` and ``credit`` tables.
        k: Forecast horizon in trading days.
        q: Trailing quantile defining "high" turbulence.
        thr_window: Trailing window for the causal threshold / percentile.

    Returns:
        ``(features, labels, feature_columns)`` aligned on a common index; rows with any NaN
        (warm-up or the final ``k`` unlabeled days) are dropped.
    """
    rets = store.read("returns").dropna(how="any")
    turb = store.read("turbulence")["turbulence"].reindex(rets.index)
    credit = store.read("credit").reindex(rets.index).ffill()

    log_turb = np.log1p(turb)
    turb_pct = turb.rolling(thr_window, min_periods=MIN_THRESHOLD_OBS).apply(
        lambda x: float((x <= x[-1]).mean()), raw=True
    )
    threshold = turb.rolling(thr_window, min_periods=MIN_THRESHOLD_OBS).quantile(q)

    feats = pd.DataFrame(index=rets.index)
    feats["log_turb"] = log_turb
    feats["turb_pct"] = turb_pct
    feats["turb_mom5"] = log_turb - log_turb.shift(5)
    feats["turb_mom21"] = log_turb - log_turb.shift(21)
    feats["rvol_spy5"] = rets["SPY"].rolling(5).std()
    feats["rvol_spy21"] = rets["SPY"].rolling(21).std()
    feats["rvol_eem21"] = rets["EEM"].rolling(21).std()
    feats["disp"] = rets.std(axis=1)
    feats["disp5"] = rets.std(axis=1).rolling(5).mean()
    feats["spy_ret5"] = rets["SPY"].rolling(5).sum()
    feats["spy_ret21"] = rets["SPY"].rolling(21).sum()
    feats["credit"] = credit["credit_stress"]
    feats["hyg_lqd"] = credit["hyg_lqd_ratio"]
    feats["credit_mom21"] = credit["credit_stress"] - credit["credit_stress"].shift(21)

    above = (turb >= threshold).astype(float)
    # 1 if turbulence is above threshold any time in t+1..t+k (forward window, causal label)
    labels = above[::-1].rolling(k, min_periods=1).max()[::-1].shift(-1).rename("y")

    data = feats.join(labels).dropna()
    feature_cols = list(feats.columns)
    logger.info("Exceedance dataset: %d rows, base rate=%.3f (k=%d, q=%.2f)",
                len(data), float(data["y"].mean()), k, q)
    return data[feature_cols], data["y"], feature_cols


def walk_forward_probabilities(
    features: pd.DataFrame,
    labels: pd.Series,
    k: int = EXCEEDANCE_HORIZON,
    refit_every: int = 21,
    min_train: int = 400,
    start: int = 504,
    C: float = REGULARIZATION_C,
) -> pd.Series:
    """Leak-safe out-of-sample exceedance probabilities via expanding-window walk-forward.

    At each refit the model trains only on rows whose ``k``-day label window has fully elapsed
    (``features.iloc[:i - k]``), then scores the next ``refit_every`` days. A fresh
    ``StandardScaler`` is fit per fold on training rows only.

    Args:
        features: Causal feature matrix (from :func:`build_exceedance_dataset`).
        labels: Aligned forward-exceedance labels.
        k: Forecast horizon (rows within ``k`` of ``i`` are excluded from training).
        refit_every: Refit/scoring cadence in days.
        min_train: Minimum training rows before scoring begins.
        start: First index scored.
        C: Inverse L2 regularization strength for the logistic regression.

    Returns:
        Out-of-sample exceedance probability indexed by date.
    """
    X = features.to_numpy()
    y = labels.to_numpy()
    preds = pd.Series(index=features.index, dtype=float)
    n = len(features)
    i = start
    while i < n:
        train_end = max(0, i - k)
        if train_end < min_train:
            i += refit_every
            continue
        scaler = StandardScaler().fit(X[:train_end])
        model = LogisticRegression(max_iter=2000, C=C)
        model.fit(scaler.transform(X[:train_end]), y[:train_end])
        block = slice(i, min(i + refit_every, n))
        preds.iloc[block] = model.predict_proba(scaler.transform(X[block]))[:, 1]
        i += refit_every
    return preds.dropna()


def latest_exceedance_probability(store, k: int = EXCEEDANCE_HORIZON) -> float | None:
    """Train on all labeled history and return today's exceedance probability, or None.

    Intended for live serving (the most recent ``k`` days are unlabeled, so they are excluded
    from training and the model scores the latest feature row).
    """
    features, labels, cols = build_exceedance_dataset(store, k=k)
    if len(features) < 450:
        return None
    scaler = StandardScaler().fit(features.to_numpy())
    model = LogisticRegression(max_iter=2000, C=REGULARIZATION_C)
    model.fit(scaler.transform(features.to_numpy()), labels.to_numpy())
    latest = scaler.transform(features.to_numpy()[-1:])
    return float(model.predict_proba(latest)[0, 1])
