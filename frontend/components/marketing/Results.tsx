"use client";

import { LADDER, CRISES, PERIOD, COST_BPS } from "@/lib/results";
import { pct } from "@/lib/format";
import { Reveal } from "@/components/motion/Reveal";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { CrisisBars } from "@/components/charts/dynamic";

export function Results() {
  return (
    <section id="results" className="mx-auto max-w-6xl px-6 py-20">
      <Reveal>
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">What each layer buys you</h2>
        <p className="mt-2 max-w-2xl text-text-secondary">
          Leak-safe walk-forward, {PERIOD}, net of {COST_BPS} bps. Every layer is judged against the
          layer below it — the turbulence overlay must beat naive vol-targeting to justify itself.
        </p>
      </Reveal>

      <Reveal delay={0.05}>
        <div className="mt-8 overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-white/[0.02] text-xs uppercase tracking-wide text-text-muted">
                <th className="px-4 py-3 text-left font-medium">Configuration</th>
                <th className="px-4 py-3 text-right font-medium">Sharpe</th>
                <th className="px-4 py-3 text-right font-medium">Ann. vol</th>
                <th className="px-4 py-3 text-right font-medium">Max drawdown</th>
                <th className="px-4 py-3 text-right font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {LADDER.map((r, i) => {
                const best = i === LADDER.length - 1;
                return (
                  <tr
                    key={r.name}
                    className={`border-b border-border/50 last:border-0 ${best ? "bg-accent/[0.06]" : ""}`}
                  >
                    <td className={`px-4 py-3 ${best ? "font-medium text-accent" : "text-text-primary"}`}>{r.name}</td>
                    <td className="tabular px-4 py-3 text-right">{r.sharpe.toFixed(3)}</td>
                    <td className="tabular px-4 py-3 text-right text-text-secondary">{pct(r.annVol, 1)}</td>
                    <td className="tabular px-4 py-3 text-right text-text-secondary">{pct(r.maxDrawdown, 1)}</td>
                    <td className="px-4 py-3 text-right text-xs text-text-muted">{r.note}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Reveal>

      <Reveal delay={0.1}>
        <div className="mt-8">
          <ChartFrame
            title="Crisis defense — total return through major drawdowns"
            subtitle="Strategy (expanded + momentum) vs equal-weight vs SPY buy-and-hold"
            height={340}
          >
            <CrisisBars data={CRISES} />
          </ChartFrame>
        </div>
      </Reveal>
    </section>
  );
}
