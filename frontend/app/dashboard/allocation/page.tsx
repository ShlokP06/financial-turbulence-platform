"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useApi, useDebounced } from "@/lib/hooks";
import { pct } from "@/lib/format";
import { GlassCard } from "@/components/ui/GlassCard";
import { Stat } from "@/components/ui/Stat";
import { Slider } from "@/components/ui/Slider";
import { Skeleton } from "@/components/ui/Skeleton";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { Notice } from "@/components/ui/Notice";
import { Reveal } from "@/components/motion/Reveal";
import { WeightsDonut, EquityCurve } from "@/components/charts/dynamic";

export default function Allocation() {
  const [tv, setTv] = useState(0.03);
  const debouncedTv = useDebounced(tv, 250);
  const weights = useApi(() => api.weights(debouncedTv), [debouncedTv]);
  const backtest = useApi(() => api.backtest());

  const entries = weights.data
    ? Object.entries(weights.data.weights).sort((a, b) => b[1] - a[1])
    : [];
  const max = entries.length ? entries[0][1] : 1;
  const hhi = entries.reduce((s, [, w]) => s + w * w, 0);
  const effectiveN = hhi > 0 ? 1 / hhi : 0;

  const bt = backtest.data;
  const btRows: [string, string, string][] = bt
    ? [
        ["Annualized return", pct(bt.strategy.ann_return, 1), pct(bt.benchmark.ann_return, 1)],
        ["Sharpe", bt.strategy.sharpe.toFixed(2), bt.benchmark.sharpe.toFixed(2)],
        ["Sortino", bt.strategy.sortino.toFixed(2), bt.benchmark.sortino.toFixed(2)],
        ["Max drawdown", pct(bt.strategy.max_drawdown, 1), pct(bt.benchmark.max_drawdown, 1)],
        ["CVaR 95% (daily)", pct(bt.strategy.cvar_95, 2), pct(bt.benchmark.cvar_95, 2)],
        ["Ann. turnover", `${bt.strategy.turnover.toFixed(1)}×`, `${bt.benchmark.turnover.toFixed(1)}×`],
      ]
    : [];

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <Reveal>
        <GlassCard>
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-text-secondary">Target volatility (annualized)</span>
              <span className="tabular text-sm font-semibold text-accent">{pct(tv, 1)}</span>
            </div>
            <Slider value={tv} min={0.01} max={0.045} step={0.0025} onChange={setTv} aria-label="Target volatility" />
            <div className="flex justify-between text-xs text-text-muted">
              <span>Conservative (more cash)</span>
              <span>Aggressive (fully invested)</span>
            </div>
          </div>
        </GlassCard>
      </Reveal>

      <Reveal delay={0.05}>
        <div className="grid gap-4 sm:grid-cols-3">
          <GlassCard>
            <Stat label="Holdings" value={entries.length || "—"} sub="assets with weight > 0" />
          </GlassCard>
          <GlassCard>
            <Stat label="Top holding" value={entries.length ? entries[0][0] : "—"} sub={entries.length ? pct(entries[0][1], 1) : undefined} />
          </GlassCard>
          <GlassCard>
            <Stat label="Effective N" value={effectiveN ? effectiveN.toFixed(1) : "—"} sub="diversification (1 / HHI)" tone="accent" />
          </GlassCard>
        </div>
      </Reveal>

      <Reveal delay={0.05}>
        <div className="grid gap-4 lg:grid-cols-2">
          <ChartFrame title="Weights" subtitle="Recommended allocation" height={320}>
            {weights.loading && !weights.data ? (
              <Skeleton className="h-full" />
            ) : weights.data ? (
              <WeightsDonut weights={weights.data.weights} />
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-text-muted">Couldn&apos;t reach the backend.</div>
            )}
          </ChartFrame>

          <GlassCard title="Breakdown">
            <ul className="flex flex-col gap-2.5">
              {entries.length === 0 && <Skeleton className="h-40" />}
              {entries.map(([name, w]) => (
                <li key={name} className="flex items-center gap-3 text-sm">
                  <span className="w-12 shrink-0 text-text-secondary">{name}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-bg-3">
                    <div
                      className="h-full rounded-full bg-accent transition-all duration-base ease-standard"
                      style={{ width: `${(w / max) * 100}%` }}
                    />
                  </div>
                  <span className="tabular w-14 shrink-0 text-right text-text-primary">{pct(w, 1)}</span>
                </li>
              ))}
            </ul>
          </GlassCard>
        </div>
      </Reveal>

      <Reveal delay={0.05}>
        <GlassCard title="Backtest — turbulence-managed vs equal-weight" subtitle="Walk-forward, no look-ahead, 10 bps cost">
          {backtest.loading ? (
            <Skeleton className="h-48" />
          ) : bt ? (
            <div className="flex flex-col gap-4">
              <div className="overflow-hidden rounded-md border border-border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-xs text-text-muted">
                      <th className="px-3 py-2 text-left font-medium">Metric</th>
                      <th className="px-3 py-2 text-right font-medium text-accent">Turbulence-managed</th>
                      <th className="px-3 py-2 text-right font-medium">Equal-weight</th>
                    </tr>
                  </thead>
                  <tbody>
                    {btRows.map(([label, s, b]) => (
                      <tr key={label} className="border-b border-border/50 last:border-0">
                        <td className="px-3 py-2 text-text-secondary">{label}</td>
                        <td className="tabular px-3 py-2 text-right text-text-primary">{s}</td>
                        <td className="tabular px-3 py-2 text-right text-text-secondary">{b}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="text-xs leading-relaxed text-text-muted">
                Live 14-asset engine: min-variance + vol-target + turbulence overlay + time-series
                momentum tilt. It beats equal-weight on a risk-adjusted basis — higher Sharpe and
                Sortino at roughly a quarter of the volatility and a far shallower drawdown. The edge
                is risk management, not headline return.
              </p>
            </div>
          ) : (
            <p className="text-sm text-text-muted">Couldn&apos;t load the backtest.</p>
          )}
        </GlassCard>
      </Reveal>

      <Reveal delay={0.05}>
        <ChartFrame title="Growth of $1" subtitle="Walk-forward equity curves, net of costs" height={300}>
          {backtest.loading ? (
            <Skeleton className="h-full" />
          ) : bt ? (
            <EquityCurve data={bt.equity} />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-text-muted">No backtest data.</div>
          )}
        </ChartFrame>
      </Reveal>

      <Notice>
        The slider retargets annualized volatility live — lower targets hold more cash. These are the
        deployed configuration (expanded 14-asset universe + momentum tilt); the Methodology page shows
        the full configuration ladder and how each layer contributes.
      </Notice>
    </div>
  );
}
