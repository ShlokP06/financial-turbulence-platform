# Backtest results

Net of 10 bps, 21-day rebalance, leakage-safe walk-forward.

## 1. Full-period ladder (core 10-asset universe, 2010-2026)

| Config | sharpe | sortino | ann_return | ann_vol | max_drawdown | turnover |
|---|---|---|---|---|---|---|
| Equal-weight | 0.563 | 0.692 | 0.049 | 0.092 | -0.218 | 0.032 |
| Vol-target (no turb) | 0.644 | 0.767 | 0.032 | 0.051 | -0.170 | 0.425 |
| Turbulence-managed | 0.696 | 0.904 | 0.029 | 0.042 | -0.160 | 1.818 |

**Marginal Sharpe from the turbulence signal (vs naive vol-targeting): +0.052.**

## 2. Forecast-driven overlay (common range 2013-07-08-2026-06-24, k=10d)

| Config | sharpe | sortino | ann_return | ann_vol | max_drawdown | turnover |
|---|---|---|---|---|---|---|
| Vol-target | 0.595 | 0.708 | 0.030 | 0.053 | -0.170 | 0.425 |
| Contemporaneous | 0.630 | 0.821 | 0.027 | 0.044 | -0.160 | 1.818 |
| Forecast-driven | 0.694 | 0.921 | 0.029 | 0.043 | -0.150 | 1.278 |

## 3. Time-series momentum tilt (core 10-asset universe)

| Config | sharpe | sortino | ann_return | ann_vol | max_drawdown | turnover |
|---|---|---|---|---|---|---|
| Base (no mom) | 0.696 | 0.904 | 0.029 | 0.042 | -0.160 | 1.818 |
| +Mom continuous | 0.706 | 0.915 | 0.029 | 0.042 | -0.148 | 2.038 |
| +Mom sign | 0.740 | 0.943 | 0.031 | 0.042 | -0.102 | 2.623 |

Sub-period Sharpe (robustness):

| Config | 2010-15 | 2016-20 | 2021-26 |
|---|---|---|---|
| Base (no mom) | 0.59 | 1.44 | 0.34 |
| +Mom continuous | 0.74 | 1.33 | 0.34 |
| +Mom sign | 0.95 | 0.92 | 0.48 |

Crisis max-drawdown:

| Config | COVID | 2022 bear | Iran war |
|---|---|---|---|
| Base (no mom) | -7.1% | -14.9% | -1.3% |
| +Mom continuous | -6.6% | -14.0% | -1.7% |
| +Mom sign | -7.1% | -8.3% | -1.3% |

## 4. Expanded 14-asset universe (core + BIL/TIP/USO/EMB)

| Config | sharpe | sortino | ann_return | ann_vol | max_drawdown | turnover |
|---|---|---|---|---|---|---|
| Base (no mom) | 0.714 | 0.912 | 0.018 | 0.025 | -0.103 | 1.829 |
| +Mom continuous | 0.822 | 1.048 | 0.019 | 0.024 | -0.088 | 2.016 |
| +Mom sign | 0.826 | 0.976 | 0.024 | 0.029 | -0.098 | 2.865 |

Sub-period Sharpe (robustness):

| Config | 2010-15 | 2016-20 | 2021-26 |
|---|---|---|---|
| Base (no mom) | 0.44 | 1.56 | 0.41 |
| +Mom continuous | 0.56 | 1.55 | 0.57 |
| +Mom sign | 0.85 | 1.10 | 0.62 |

Crisis max-drawdown:

| Config | COVID | 2022 bear | Iran war |
|---|---|---|---|
| Base (no mom) | -4.5% | -9.4% | -0.9% |
| +Mom continuous | -3.7% | -8.3% | -0.7% |
| +Mom sign | -4.4% | -9.5% | -0.9% |
