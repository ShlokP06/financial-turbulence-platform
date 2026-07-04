"""Run the turbulence-managed strategy backtests and write the results artifact.

Usage: python scripts/run_backtest.py

Produces `reports/RESULTS.md` and `reports/backtest_results.json` covering:
  1. Full-period ladder (equal-weight -> vol-target -> turbulence overlay), leak-safe, net of costs.
  2. Forecast-driven overlay vs contemporaneous (isolates the forecast signal's value).
  3. Time-series momentum tilt (continuous / sign) on the core 10-asset universe.
  4. The same on the expanded 14-asset universe (if `features_expanded.duckdb` exists),
     with sub-period robustness and crisis drawdowns.
"""
from __future__ import annotations

import json
from pathlib import Path

from turballoc.allocation.strategy import CASH, turbulence_managed_weights
from turballoc.backtest.engine import (
    _ann_turnover,
    run_forecast_backtest,
    run_strategy_backtest,
    walk_forward_backtest,
)
from turballoc.backtest.metrics import max_drawdown, summary
from turballoc.ingest.store import FeatureStore

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
EXPANDED_DB = ROOT / "data" / "processed" / "features_expanded.duckdb"
METRICS = ["sharpe", "sortino", "ann_return", "ann_vol", "max_drawdown", "turnover"]
SUBPERIODS = {"2010-15": ("2010", "2015"), "2016-20": ("2016", "2020"), "2021-26": ("2021", "2026")}
CRISES = {"COVID": ("2020-02-19", "2020-04-30"), "2022 bear": ("2022-01-03", "2022-10-12"),
          "Iran war": ("2026-02-28", "2026-06-25")}


def _strategy_port(store, momentum=None, lookback=252, rebalance=21, cost=0.001, rf=0.02, tv=0.07):
    """Daily return series + one-way turnover for the turbulence-managed strategy."""
    returns = store.read("returns").dropna(how="any")
    turb = store.read("turbulence").dropna(subset=["turbulence"])["turbulence"]
    risky = list(returns.columns)
    r = returns.copy()
    r[CASH] = (1 + rf) ** (1 / 252) - 1

    def fn(window):
        win = window[risky].iloc[-lookback:].dropna(how="any")
        return turbulence_managed_weights(win, turb.loc[: window.index[-1]],
                                          momentum=momentum, target_vol=tv)

    port, wlog, _ = walk_forward_backtest(r, fn, lookback, rebalance, cost)
    return port, _ann_turnover(wlog, rebalance) / 2.0


def _momentum_table(store, label):
    """Full-period stats, sub-period Sharpe, and crisis drawdowns for base/continuous/sign."""
    out = {}
    for mode_label, mode in (("Base (no mom)", None), ("+Mom continuous", "continuous"),
                             ("+Mom sign", "sign")):
        port, turn = _strategy_port(store, momentum=mode)
        stats = summary(port)
        stats["turnover"] = turn
        stats["subperiod_sharpe"] = {k: summary(port.loc[a:b])["sharpe"] for k, (a, b) in SUBPERIODS.items()}
        stats["crisis_maxdd"] = {k: max_drawdown(port.loc[a:b]) for k, (a, b) in CRISES.items()}
        out[mode_label] = stats
    return out


def _print_block(title, table):
    print(f"\n{title}")
    print(f"{'config':<18}" + "".join(f"{m:>12}" for m in METRICS))
    for name, s in table.items():
        print(f"{name:<18}" + "".join(f"{s[m]:>12.3f}" for m in METRICS))


def _md_table(table):
    md = ["| Config | " + " | ".join(METRICS) + " |", "|" + "---|" * (len(METRICS) + 1)]
    for name, s in table.items():
        md.append("| " + name + " | " + " | ".join(f"{s[m]:.3f}" for m in METRICS) + " |")
    return md


def _md_subperiods(table):
    md = ["| Config | " + " | ".join(SUBPERIODS) + " |", "|" + "---|" * (len(SUBPERIODS) + 1)]
    for name, s in table.items():
        md.append("| " + name + " | " + " | ".join(f"{s['subperiod_sharpe'][k]:.2f}" for k in SUBPERIODS) + " |")
    return md


def _md_crises(table):
    md = ["| Config | " + " | ".join(CRISES) + " |", "|" + "---|" * (len(CRISES) + 1)]
    for name, s in table.items():
        md.append("| " + name + " | " + " | ".join(f"{s['crisis_maxdd'][k]:.1%}" for k in CRISES) + " |")
    return md


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    core = FeatureStore()

    # 1. full-period ladder + marginal turbulence value
    res = run_strategy_backtest(core)
    ladder = {"Equal-weight": res["benchmark"], "Vol-target (no turb)": res["vol_target"],
              "Turbulence-managed": res["strategy"]}
    _print_block("Full-period ladder (core 10):", ladder)
    turb_alpha = res["strategy"]["sharpe"] - res["vol_target"]["sharpe"]
    print(f"Marginal Sharpe from turbulence vs vol-target: {turb_alpha:+.3f}")

    # 2. forecast-driven overlay
    fc = run_forecast_backtest(core)
    fc_tab = {"Vol-target": fc["vol_target"], "Contemporaneous": fc["contemporaneous"],
              "Forecast-driven": fc["forecast"]}
    _print_block(f"Forecast overlay ({fc['common_start']}->{fc['common_end']}, k={fc['horizon_days']}d):", fc_tab)

    # 3 & 4. momentum on core and expanded universes
    mom_core = _momentum_table(core, "core")
    _print_block("Momentum tilt (core 10):", mom_core)
    mom_exp = None
    if EXPANDED_DB.exists():
        mom_exp = _momentum_table(FeatureStore(EXPANDED_DB), "expanded")
        _print_block("Momentum tilt (expanded 14):", mom_exp)

    # ---- write artifacts ----
    md = ["# Backtest results", "",
          f"Net of {res['cost_bps']:.0f} bps, {res['rebalance_days']}-day rebalance, leakage-safe walk-forward.",
          "", "## 1. Full-period ladder (core 10-asset universe, 2010-2026)", "", *_md_table(ladder),
          "", f"**Marginal Sharpe from the turbulence signal (vs naive vol-targeting): {turb_alpha:+.3f}.**",
          "", f"## 2. Forecast-driven overlay (common range {fc['common_start']}-{fc['common_end']}, k={fc['horizon_days']}d)",
          "", *_md_table(fc_tab),
          "", "## 3. Time-series momentum tilt (core 10-asset universe)", "", *_md_table(mom_core),
          "", "Sub-period Sharpe (robustness):", "", *_md_subperiods(mom_core),
          "", "Crisis max-drawdown:", "", *_md_crises(mom_core)]
    if mom_exp is not None:
        md += ["", "## 4. Expanded 14-asset universe (core + BIL/TIP/USO/EMB)", "", *_md_table(mom_exp),
               "", "Sub-period Sharpe (robustness):", "", *_md_subperiods(mom_exp),
               "", "Crisis max-drawdown:", "", *_md_crises(mom_exp)]
    (REPORTS / "RESULTS.md").write_text("\n".join(md) + "\n")
    (REPORTS / "backtest_results.json").write_text(json.dumps(
        {"full_period": res, "forecast_overlay": fc, "momentum_core": mom_core,
         "momentum_expanded": mom_exp}, indent=2, default=float))
    print(f"\nWrote {REPORTS / 'RESULTS.md'} and backtest_results.json")


if __name__ == "__main__":
    main()
