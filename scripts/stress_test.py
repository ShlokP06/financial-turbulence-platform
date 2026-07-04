"""Crisis stress-test of the best config (expanded universe + continuous momentum tilt).

Compares the strategy against equal-weight and a buy-and-hold SPY reference across major
stress episodes, reporting window return and max drawdown. Writes reports/STRESS.md.

Usage: python scripts/stress_test.py
"""
from __future__ import annotations

import json
from pathlib import Path

from turballoc.allocation.strategy import CASH, turbulence_managed_weights
from turballoc.backtest.engine import walk_forward_backtest
from turballoc.backtest.metrics import max_drawdown
from turballoc.ingest.store import FeatureStore

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
EXPANDED_DB = ROOT / "data" / "processed" / "features_expanded.duckdb"
LB, REBAL, COST, RF, TV = 252, 21, 0.001, 0.02, 0.07

CRISES = {
    "GFC aftershock / Euro crisis (2011)": ("2011-07-01", "2011-10-04"),
    "2015-16 China / oil rout": ("2015-08-01", "2016-02-11"),
    "2018 Q4 selloff": ("2018-09-20", "2018-12-24"),
    "COVID crash (peak->trough)": ("2020-02-19", "2020-03-23"),
    "2022 bear (rates shock)": ("2022-01-03", "2022-10-12"),
    "2026 Iran war oil shock": ("2026-02-28", "2026-03-31"),
}


def _port(store, momentum=None):
    returns = store.read("returns").dropna(how="any")
    turb = store.read("turbulence").dropna(subset=["turbulence"])["turbulence"]
    risky = list(returns.columns)
    r = returns.copy()
    r[CASH] = (1 + RF) ** (1 / 252) - 1

    def fn(window):
        win = window[risky].iloc[-LB:].dropna(how="any")
        return turbulence_managed_weights(win, turb.loc[: window.index[-1]],
                                          momentum=momentum, target_vol=TV)

    port, _, _ = walk_forward_backtest(r, fn, LB, REBAL, COST)
    return port


def main() -> None:
    store = FeatureStore(EXPANDED_DB) if EXPANDED_DB.exists() else FeatureStore()
    universe = "expanded 14-asset" if EXPANDED_DB.exists() else "core 10-asset"
    returns = store.read("returns").dropna(how="any")
    spy = returns["SPY"]
    eqw = returns.mean(axis=1)  # equal-weight daily return
    base = _port(store, momentum=None)
    best = _port(store, momentum="continuous")
    series = {"SPY (buy & hold)": spy, "Equal-weight": eqw,
              "Strategy (base)": base, "Strategy (+momentum)": best}

    def cum(s, a, b):
        return float((1 + s.loc[a:b]).prod() - 1)

    names = list(series)
    rows_ret, rows_dd = [], []
    for label, (a, b) in CRISES.items():
        rows_ret.append([label] + [cum(series[n], a, b) for n in names])
        rows_dd.append([label] + [max_drawdown(series[n].loc[a:b]) for n in names])

    def show(title, rows):
        print(f"\n{title}")
        print(f"{'window':<38}" + "".join(f"{n:>22}" for n in names))
        for row in rows:
            print(f"{row[0]:<38}" + "".join(f"{x:>22.1%}" for x in row[1:]))

    show("Total return through crisis windows:", rows_ret)
    show("Max drawdown within crisis windows:", rows_dd)

    REPORTS.mkdir(exist_ok=True)
    md = [f"# Crisis stress tests ({universe})", "",
          "Best config = minimum-variance base + vol-targeting + turbulence overlay + continuous",
          "time-series momentum tilt. Leak-safe walk-forward, net of costs. SPY and equal-weight",
          "shown as references.", "",
          "## Total return through crisis windows", "",
          "| Window | " + " | ".join(names) + " |", "|" + "---|" * (len(names) + 1)]
    for row in rows_ret:
        md.append("| " + row[0] + " | " + " | ".join(f"{x:.1%}" for x in row[1:]) + " |")
    md += ["", "## Max drawdown within crisis windows", "",
           "| Window | " + " | ".join(names) + " |", "|" + "---|" * (len(names) + 1)]
    for row in rows_dd:
        md.append("| " + row[0] + " | " + " | ".join(f"{x:.1%}" for x in row[1:]) + " |")
    md += ["", "Note: a contemporaneous/short-horizon signal cushions but cannot fully dodge",
           "2-week crashes (COVID), and the 2022 rates shock — where bonds and equities fell",
           "together — is the hardest regime. The strategy gives up upside in sharp recoveries."]
    (REPORTS / "STRESS.md").write_text("\n".join(md) + "\n")
    (REPORTS / "stress_results.json").write_text(json.dumps(
        {"universe": universe,
         "return": {r[0]: dict(zip(names, r[1:])) for r in rows_ret},
         "max_drawdown": {r[0]: dict(zip(names, r[1:])) for r in rows_dd}}, indent=2, default=float))
    print(f"\nWrote {REPORTS / 'STRESS.md'} and stress_results.json")


if __name__ == "__main__":
    main()
