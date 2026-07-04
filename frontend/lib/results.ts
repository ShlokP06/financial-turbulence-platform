/**
 * Static, sourced research numbers — copied verbatim from `reports/RESULTS.md` and
 * `reports/STRESS.md` (leak-safe walk-forward, net of 10 bps, 21-day rebalance).
 *
 * Two configs are distinguished so nothing is misrepresented:
 *  - RESEARCH_BEST: the deployed engine — expanded 14-asset universe + min-variance + vol-target
 *    + turbulence overlay + continuous momentum tilt. This is what the /backtest and /weights
 *    endpoints serve, so the Allocation page shows these same figures live.
 *  - LIVE_BASE: a reference row for the core 10-asset "turbulence only, no momentum" config,
 *    used in the Methodology ladder to isolate each layer's contribution. Not served.
 *
 * The Methodology "configuration ladder" connects them transparently.
 */

export interface MetricSet {
  sharpe: number;
  sortino: number;
  annReturn: number;
  annVol: number;
  maxDrawdown: number;
  turnover: number;
}

/** Reference config — core 10-asset, turbulence overlay, no momentum (not served; ladder only). */
export const LIVE_BASE = {
  strategy: {
    sharpe: 0.696,
    sortino: 0.904,
    annReturn: 0.029,
    annVol: 0.042,
    maxDrawdown: -0.16,
    turnover: 1.818,
  } as MetricSet,
  benchmark: {
    sharpe: 0.563,
    sortino: 0.692,
    annReturn: 0.049,
    annVol: 0.092,
    maxDrawdown: -0.218,
    turnover: 0.032,
  } as MetricSet,
};

/** Best validated configuration — expanded 14-asset + continuous momentum (offline research). */
export const RESEARCH_BEST: MetricSet = {
  sharpe: 0.822,
  sortino: 1.048,
  annReturn: 0.019,
  annVol: 0.024,
  maxDrawdown: -0.088,
  turnover: 2.016,
};

/** Configuration ladder (RESULTS.md §1 + §4) — how each layer moves risk-adjusted return. */
export const LADDER: { name: string; sharpe: number; annVol: number; maxDrawdown: number; note: string }[] = [
  { name: "Equal-weight", sharpe: 0.563, annVol: 0.092, maxDrawdown: -0.218, note: "benchmark" },
  { name: "Naive vol-target", sharpe: 0.644, annVol: 0.051, maxDrawdown: -0.17, note: "risk control only" },
  { name: "Turbulence-managed", sharpe: 0.696, annVol: 0.042, maxDrawdown: -0.16, note: "turbulence only" },
  { name: "+ Momentum (expanded 14)", sharpe: 0.822, annVol: 0.024, maxDrawdown: -0.088, note: "live engine" },
];

/** Out-of-sample skill of the exceedance model vs persistence (from the forecast study). */
export const EXCEEDANCE = {
  auc: 0.71,
  persistenceAuc: 0.69,
  horizonDays: 10,
};

export interface CrisisRow {
  window: string;
  spy: number; // total return over the window
  equalWeight: number;
  strategyBase: number;
  strategyMomentum: number;
}

/** Total return through crisis windows (STRESS.md, expanded 14-asset best config). */
export const CRISES: CrisisRow[] = [
  { window: "Euro crisis (2011)", spy: -0.157, equalWeight: -0.064, strategyBase: -0.004, strategyMomentum: -0.005 },
  { window: "China / oil rout (2015–16)", spy: -0.131, equalWeight: -0.102, strategyBase: -0.015, strategyMomentum: -0.014 },
  { window: "Q4 2018 selloff", spy: -0.192, equalWeight: -0.082, strategyBase: -0.005, strategyMomentum: -0.005 },
  { window: "COVID crash (2020)", spy: -0.354, equalWeight: -0.219, strategyBase: -0.032, strategyMomentum: -0.025 },
  { window: "2022 bear (rates shock)", spy: -0.258, equalWeight: -0.157, strategyBase: -0.093, strategyMomentum: -0.081 },
  { window: "Iran war oil shock (2026)", spy: -0.051, equalWeight: 0.002, strategyBase: -0.003, strategyMomentum: -0.003 },
];

export const UNIVERSE_CORE = ["SPY", "EFA", "EEM", "AGG", "TLT", "LQD", "HYG", "DBC", "GLD", "VNQ"];
export const UNIVERSE_EXTRA = ["BIL", "TIP", "USO", "EMB"];

export const PERIOD = "2010–2026";
export const COST_BPS = 10;
