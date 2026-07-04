import numpy as np
import pandas as pd
from turballoc.allocation.covariance import shrunk_covariance
from turballoc.allocation.risk_based import min_variance_weights
from turballoc.allocation.strategy import (
    CASH,
    turbulence_managed_weights,
    vol_target_scale,
)
from turballoc.backtest.metrics import TRADING_DAYS, summary
from turballoc.forecast.exceedance import (
    EXCEEDANCE_HORIZON,
    build_exceedance_dataset,
    walk_forward_probabilities,
)
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def walk_forward_backtest(returns, weight_fn, lookback = 252, rebalance = 21, cost = 0.001):
    """
    Walk-forward backtest with no lookahead. 
    At each rebalance step, weight_fn sees ONLY returns.iloc[:i] and
    returns target weights, applied to forward returns until the next
    rebalance. A linear transaction cost is charged on L1 weight turnover
    at each rebalance.
    
    Returns (portfolio_returns, weight_log, stats).
    """

    dates = returns.index
    weights = pd.Series(np.zeros(returns.shape[1]), index = returns.columns)
    port = pd.Series(0.0, index = dates)
    weight_log = {}
    
    for i in range(lookback, len(dates)):
        if (i - lookback) % rebalance == 0:
            target = weight_fn(returns.iloc[:i])    #only past, no leakage
            target = target.reindex(returns.columns).fillna(0.0)
            turnover = (target - weights).abs().sum()
            port.iloc[i] = -cost * turnover
            weights = target
            weight_log[dates[i]] = weights
        port.iloc[i] += float((weights * returns.iloc[i]).sum())
    port = port.iloc[lookback:]
    stats = summary(port)
    logger.info("Backtest: sharpe = %.2f maxDD = %.1f%%", stats["sharpe"], 100 * stats["max_drawdown"])
    return port, pd.DataFrame(weight_log).T, stats

def _ann_turnover(weight_log, rebalance):
    "Annualized two-way (L1) turnover from the per-rebalance weight log; halve for one-way."
    if weight_log.empty:
        return 0.0
    steps = weight_log.diff().abs().sum(axis=1)
    steps.iloc[0] = weight_log.iloc[0].abs().sum()  # first trade is from cash
    return float(steps.mean() * (TRADING_DAYS / rebalance))

def _equity_points(strat, bench, max_points = 240):
    "Aligned, downsampled equity curves for charting: [{date, strategy, benchmark}]."
    eq_s = (1 + strat).cumprod()
    eq_b = (1 + bench).cumprod()
    step = max(1, len(eq_s) // max_points)
    out = []
    for i in range(0, len(eq_s), step):
        out.append({"date": eq_s.index[i].date().isoformat(),
                    "strategy": float(eq_s.iloc[i]), "benchmark": float(eq_b.iloc[i])})
    return out

def run_strategy_backtest(
    store,
    lookback = 252,
    rebalance = 21,
    cost = 0.001,
    rf_annual = 0.02,
    target_vol = 0.07,
    momentum = None,       # None | "continuous" | "sign" -> time-series momentum tilt on the base
    risk_aversion = 2.5,   # kept for backward compatibility; unused by the managed strategy
):
    """Walk-forward backtest of the turbulence-managed risk-parity strategy.

    Compares three configs rebalanced on the same schedule with the same cost model, all
    leakage-safe (each rebalance sees only returns and turbulence up to that date):
      - ``strategy``: Ledoit-Wolf min-variance + vol-targeting + turbulence exposure overlay
      - ``benchmark``: equal-weight (the naive baseline)
      - ``vol_target``: same base + vol-targeting but NO turbulence — isolates the marginal
        value of the turbulence signal

    The de-risked sleeve is modeled as a synthetic ``CASH`` asset earning ``rf_annual``.
    Reported turnover is conventional one-way (half the L1 weight change).
    """
    returns = store.read("returns").dropna(how="any")
    if "turbulence" in store.list_tables():
        turb = store.read("turbulence").dropna(subset=["turbulence"])["turbulence"]
    else:
        turb = pd.Series(dtype=float)
    risky = list(returns.columns)
    n = len(risky)

    # Synthetic cash sleeve so the de-risked fraction earns the risk-free rate.
    rf_daily = (1 + rf_annual) ** (1 / TRADING_DAYS) - 1
    r = returns.copy()
    r[CASH] = rf_daily

    def _window(window):
        return window[risky].iloc[-lookback:].dropna(how="any")

    def strategy_fn(window):
        return turbulence_managed_weights(
            _window(window), turb.loc[: window.index[-1]],
            momentum=momentum, target_vol=target_vol,
        )

    def equal_fn(window):
        return pd.Series(np.ones(n) / n, index=risky)

    def vol_target_fn(window):
        cov = shrunk_covariance(_window(window), annualize=True)
        w = min_variance_weights(cov)
        exposure = vol_target_scale(w, cov, target_vol)
        w = w * exposure
        w[CASH] = 1.0 - exposure
        return w

    strat_ret, strat_w, strat_stats = walk_forward_backtest(r, strategy_fn, lookback, rebalance, cost)
    bench_ret, bench_w, bench_stats = walk_forward_backtest(r, equal_fn, lookback, rebalance, cost)
    vt_ret, vt_w, vt_stats = walk_forward_backtest(r, vol_target_fn, lookback, rebalance, cost)
    strat_stats["turnover"] = _ann_turnover(strat_w, rebalance) / 2.0
    bench_stats["turnover"] = _ann_turnover(bench_w, rebalance) / 2.0
    vt_stats["turnover"] = _ann_turnover(vt_w, rebalance) / 2.0
    return {
        "strategy": strat_stats,
        "benchmark": bench_stats,
        "vol_target": vt_stats,
        "equity": _equity_points(strat_ret, bench_ret),
        "rebalance_days": rebalance,
        "cost_bps": cost * 1e4,
    }


def run_forecast_backtest(
    store,
    k = EXCEEDANCE_HORIZON,
    lookback = 252,
    rebalance = 21,
    cost = 0.001,
    rf_annual = 0.02,
    target_vol = 0.07,
):
    """Compare the contemporaneous turbulence overlay vs a forecast-driven overlay.

    The forecast-driven overlay swaps a single signal: instead of ramping exposure on the
    contemporaneous turbulence percentile, it ramps on the trailing percentile of a leak-safe
    out-of-sample exceedance probability (logistic regression refit on an expanding window).
    All configs are compared over the common range where the forecast is available.

    Returns a dict with ``contemporaneous``, ``forecast`` and ``vol_target`` stats (one-way
    turnover included), the common date range, and the forecast horizon.
    """
    returns = store.read("returns").dropna(how="any")
    turb = store.read("turbulence").dropna(subset=["turbulence"])["turbulence"]
    features, labels, _ = build_exceedance_dataset(store, k=k)
    prob = walk_forward_probabilities(features, labels, k=k, refit_every=rebalance)

    risky = list(returns.columns)
    rf_daily = (1 + rf_annual) ** (1 / TRADING_DAYS) - 1
    r = returns.copy()
    r[CASH] = rf_daily

    def _window(window):
        return window[risky].iloc[-lookback:].dropna(how="any")

    def contemp_fn(window):
        return turbulence_managed_weights(_window(window), turb.loc[: window.index[-1]],
                                          target_vol=target_vol)

    def forecast_fn(window):
        return turbulence_managed_weights(_window(window), turb.loc[: window.index[-1]],
                                          overlay_history=prob.loc[: window.index[-1]],
                                          target_vol=target_vol)

    def vol_target_fn(window):
        cov = shrunk_covariance(_window(window), annualize=True)
        w = min_variance_weights(cov)
        exposure = vol_target_scale(w, cov, target_vol)
        w = w * exposure
        w[CASH] = 1.0 - exposure
        return w

    common = prob.index.min()
    out = {}
    for name, fn in (("contemporaneous", contemp_fn), ("forecast", forecast_fn),
                     ("vol_target", vol_target_fn)):
        port, wlog, _ = walk_forward_backtest(r, fn, lookback, rebalance, cost)
        stats = summary(port.loc[common:])
        stats["turnover"] = _ann_turnover(wlog, rebalance) / 2.0
        out[name] = stats
    out["common_start"] = str(common.date())
    out["common_end"] = str(prob.index.max().date())
    out["horizon_days"] = k
    return out