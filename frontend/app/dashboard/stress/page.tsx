"use client";

import { CRISES, PERIOD, COST_BPS } from "@/lib/results";
import { pct } from "@/lib/format";
import { GlassCard } from "@/components/ui/GlassCard";
import { Notice } from "@/components/ui/Notice";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { Reveal } from "@/components/motion/Reveal";
import { CrisisBars } from "@/components/charts/dynamic";
import { cn } from "@/lib/cn";

function Ret({ x }: { x: number }) {
  return <span className={cn("tabular", x < -0.02 ? "text-neg" : x < 0 ? "text-text-primary" : "text-pos")}>{pct(x, 1)}</span>;
}

export default function Stress() {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <Reveal>
        <ChartFrame
          title="Crisis defense — total return through major drawdowns"
          subtitle="Strategy (expanded + momentum) vs equal-weight vs SPY buy-and-hold"
          height={340}
        >
          <CrisisBars data={CRISES} />
        </ChartFrame>
      </Reveal>

      <Reveal delay={0.05}>
        <GlassCard title="Full crisis ledger" subtitle={`Total return through each window · leak-safe walk-forward, net of ${COST_BPS} bps`}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-xs uppercase tracking-wide text-text-muted">
                  <th className="px-3 py-2 text-left font-medium">Crisis window</th>
                  <th className="px-3 py-2 text-right font-medium">SPY</th>
                  <th className="px-3 py-2 text-right font-medium">Equal-weight</th>
                  <th className="px-3 py-2 text-right font-medium">Strategy (base)</th>
                  <th className="px-3 py-2 text-right font-medium text-accent">Strategy (+momentum)</th>
                </tr>
              </thead>
              <tbody>
                {CRISES.map((c) => (
                  <tr key={c.window} className="border-b border-border/50 last:border-0">
                    <td className="px-3 py-2.5 text-text-primary">{c.window}</td>
                    <td className="px-3 py-2.5 text-right"><Ret x={c.spy} /></td>
                    <td className="px-3 py-2.5 text-right"><Ret x={c.equalWeight} /></td>
                    <td className="px-3 py-2.5 text-right"><Ret x={c.strategyBase} /></td>
                    <td className="px-3 py-2.5 text-right"><Ret x={c.strategyMomentum} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </Reveal>

      <Notice>
        Offline study on the expanded 14-asset universe ({PERIOD}), sourced from{" "}
        <span className="font-mono text-text-primary">reports/STRESS.md</span>. A short-horizon signal
        cushions but cannot fully dodge two-week crashes (COVID); the 2022 rates shock — where bonds and
        equities fell together — is the hardest regime, and the strategy gives up upside in sharp
        recoveries. These are honest limitations, not a fitted best-case.
      </Notice>
    </div>
  );
}
