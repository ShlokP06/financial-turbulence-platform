import pandas as pd
import numpy as np

def implied_equilibrium_returns(cov, weights, risk_av = 2.5):
    "Reverse-optimize the market's implied returns: pi = delta * Sigma * w_mkt"
    pi = risk_av * cov.to_numpy() @ weights.to_numpy()
    return pd.Series(pi, index = cov.index, name = "prior")

def black_litterman(cov, pi, views_P, views_Q, tau = 0.05, omega = None):
    """Black-Litterman posterior expected returns blending prior pi with views (P, Q).
    P: (k, n) view-loading matrix, Q: (k,) view returns. Default omega assumes view
    uncertainty proportional to the views' own variance (IDzorek-style diagonal)"""

    assets = cov.index
    Sigma = cov.to_numpy()
    pi_v = pi.to_numpy().reshape(-1, 1)
    P = np.atleast_2d(np.asarray(views_P, dtype = float))
    Q = np.asarray(views_Q, dtype = float).reshape(-1, 1)
    tau_sigma = tau*Sigma
    if omega is None:
        omega = np.diag(np.diag(P @ tau_sigma @ P.T))
    omega_inv = np.linalg.inv(omega)
    prior_inv = np.linalg.inv(tau_sigma)
    post_prec = prior_inv + P.T @ omega_inv @ P
    post_mean = np.linalg.solve(post_prec, prior_inv @ pi_v + P.T @ omega_inv @ Q)
    return pd.Series(post_mean.ravel(), index = assets, name = "posterior")

def mean_variance_weights(mu, cov, risk_av = 2.5, long_only = True):
    "Unconstrained MV weights w = Sigma^-1 mu / delta, optionally clipped, normalized"
    raw = np.linalg.solve(cov.to_numpy(), mu.to_numpy()) / risk_av
    if long_only:
        raw = np.clip(raw, 0.0, None)
    total = raw.sum()
    if total == 0:
        raw = np.ones_like(raw)
        total = raw.sum()
    return pd.Series(raw / total, index = mu.index, name = "weight")