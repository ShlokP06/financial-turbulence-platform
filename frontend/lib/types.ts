export type Regime = "calm" | "normal" | "elevated" | "turbulent";

export interface Health {
  status: string;
  tables: string[];
}

export interface TurbulencePoint {
  date: string;
  turbulence: number;
  regime: Regime;
}

export interface Weights {
  weights: Record<string, number>;
  target_vol: number;
}

export interface RegimeRisk {
  probability: number;
  horizon_days: number;
  as_of: string;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

export interface Explain {
  importances: FeatureImportance[];
}

export interface AssetDriver {
  asset: string;
  ret: number;
  z: number;
}

export interface NewsSource {
  title: string;
  url: string;
  published: string;
}

export interface Why {
  date: string;
  turbulence: number;
  regime: Regime;
  drivers: AssetDriver[];
  sources: NewsSource[];
  explanation: string;
}

export interface BacktestMetrics {
  ann_return: number;
  ann_vol: number;
  sharpe: number;
  sortino: number;
  max_drawdown: number;
  cvar_95: number;
  turnover: number;
}

export interface EquityPoint {
  date: string;
  strategy: number;
  benchmark: number;
}

export interface Backtest {
  strategy: BacktestMetrics;
  benchmark: BacktestMetrics;
  equity: EquityPoint[];
  rebalance_days: number;
  cost_bps: number;
}
