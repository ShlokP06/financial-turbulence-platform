import type {
  Backtest,
  Explain,
  Health,
  RegimeRisk,
  TurbulencePoint,
  Weights,
  Why,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ApiResult<T> {
  data: T;
  /** Server-reported processing time (ms), parsed from the X-Process-Time-ms header. */
  latencyMs: number | null;
}

async function getJson<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  const res = await fetch(`${BASE}${path}`, {
    // Always hit the backend fresh; this is live signal data.
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    throw new Error(`${path} -> ${res.status} ${res.statusText}`);
  }
  const header = res.headers.get("X-Process-Time-ms");
  return {
    data: (await res.json()) as T,
    latencyMs: header ? Number(header) : null,
  };
}

export const api = {
  health: () => getJson<Health>("/health"),
  latestTurbulence: () => getJson<TurbulencePoint>("/turbulence/latest"),
  turbulenceHistory: (limit = 504) =>
    getJson<TurbulencePoint[]>(`/turbulence/history?limit=${limit}`),
  weights: (targetVol = 0.07, lookback = 252) =>
    getJson<Weights>(`/weights?target_vol=${targetVol}&lookback=${lookback}`),
  regimeRisk: () => getJson<RegimeRisk>("/regime/risk"),
  explain: () => getJson<Explain>("/explain"),
  why: (date: string) => getJson<Why>(`/turbulence/why?date=${date}`),
  backtest: () => getJson<Backtest>("/backtest"),
};
