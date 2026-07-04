"use client";

import { api } from "@/lib/api";
import { useApi } from "@/lib/hooks";
import { LADDER, EXCEEDANCE, UNIVERSE_CORE, UNIVERSE_EXTRA, PERIOD } from "@/lib/results";
import { pct } from "@/lib/format";
import { GlassCard } from "@/components/ui/GlassCard";
import { Notice } from "@/components/ui/Notice";
import { Skeleton } from "@/components/ui/Skeleton";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { Reveal } from "@/components/motion/Reveal";
import { FeatureImportanceBar } from "@/components/charts/dynamic";

const REFS = [
  "Kritzman & Li (2010) — Skulls, Financial Turbulence, and Risk Management, FAJ.",
  "Ledoit & Wolf (2004) — Honey, I Shrunk the Sample Covariance Matrix.",
  "Moskowitz, Ooi & Pedersen (2012) — Time Series Momentum, JFE.",
];

export default function Methodology() {
  const explain = useApi(() => api.explain());
  const importances = explain.data?.importances ?? [];

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <Reveal>
        <GlassCard title="Configuration ladder" subtitle={`Each layer judged against the one below · walk-forward, ${PERIOD}`}>
          <div className="overflow-hidden rounded-md border border-border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-xs uppercase tracking-wide text-text-muted">
                  <th className="px-3 py-2 text-left font-medium">Configuration</th>
                  <th className="px-3 py-2 text-right font-medium">Sharpe</th>
                  <th className="px-3 py-2 text-right font-medium">Ann. vol</th>
                  <th className="px-3 py-2 text-right font-medium">Max DD</th>
                  <th className="px-3 py-2 text-right font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {LADDER.map((r, i) => {
                  const best = i === LADDER.length - 1;
                  const live = r.note === "live engine";
                  return (
                    <tr key={r.name} className={`border-b border-border/50 last:border-0 ${best ? "bg-accent/[0.06]" : ""}`}>
                      <td className={`px-3 py-2.5 ${best ? "font-medium text-accent" : "text-text-primary"}`}>{r.name}</td>
                      <td className="tabular px-3 py-2.5 text-right">{r.sharpe.toFixed(3)}</td>
                      <td className="tabular px-3 py-2.5 text-right text-text-secondary">{pct(r.annVol, 1)}</td>
                      <td className="tabular px-3 py-2.5 text-right text-text-secondary">{pct(r.maxDrawdown, 1)}</td>
                      <td className="px-3 py-2.5 text-right text-xs">
                        <span className={live ? "text-accent" : "text-text-muted"}>{r.note}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs leading-relaxed text-text-muted">
            The dashboard serves the top <span className="text-accent">live engine</span> row — the best
            validated configuration (turbulence overlay + momentum tilt on the expanded 14-asset universe).
            Lower rows show what each layer contributes. Nothing here is cherry-picked to a single
            sub-period — see the robustness grid in the repo.
          </p>
        </GlassCard>
      </Reveal>

      <Reveal delay={0.05}>
        <ChartFrame
          title="What drives the forecast — SHAP feature importance"
          subtitle="Mean |SHAP| from a gradient-boosting surrogate over the live features"
          height={320}
        >
          {explain.loading ? (
            <Skeleton className="h-full" />
          ) : importances.length ? (
            <FeatureImportanceBar data={importances} />
          ) : (
            <div className="flex h-full items-center justify-center px-6 text-center text-sm text-text-muted">
              No explanation yet — needs the turbulence + feature tables built on the backend.
            </div>
          )}
        </ChartFrame>
      </Reveal>

      <Reveal delay={0.05}>
        <div className="grid gap-4 lg:grid-cols-2">
          <GlassCard title="Exceedance model" subtitle="The forecaster that actually works">
            <div className="flex items-end gap-6">
              <div>
                <div className="text-3xl font-semibold tabular text-accent">{EXCEEDANCE.auc.toFixed(2)}</div>
                <div className="text-xs text-text-muted">model AUC</div>
              </div>
              <div>
                <div className="text-3xl font-semibold tabular text-text-secondary">{EXCEEDANCE.persistenceAuc.toFixed(2)}</div>
                <div className="text-xs text-text-muted">persistence baseline</div>
              </div>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-text-secondary">
              A regularized logistic model predicts whether turbulence breaches a high trailing threshold
              within {EXCEEDANCE.horizonDays} days. It beats persistence out-of-sample and feeds the
              de-risk overlay. A deep LSTM-CNN <em>level</em> forecaster was built and cut — beaten by
              predicting the running mean.
            </p>
          </GlassCard>

          <GlassCard title="Universe & references">
            <div className="mb-4">
              <div className="mb-2 text-xs uppercase tracking-wide text-text-muted">Core (live)</div>
              <div className="flex flex-wrap gap-1.5">
                {UNIVERSE_CORE.map((t) => (
                  <span key={t} className="rounded border border-border bg-white/[0.03] px-2 py-0.5 font-mono text-xs text-text-secondary">{t}</span>
                ))}
              </div>
              <div className="mb-2 mt-3 text-xs uppercase tracking-wide text-text-muted">Expanded (research)</div>
              <div className="flex flex-wrap gap-1.5">
                {UNIVERSE_EXTRA.map((t) => (
                  <span key={t} className="rounded border border-accent/30 bg-accent/[0.06] px-2 py-0.5 font-mono text-xs text-accent">{t}</span>
                ))}
              </div>
            </div>
            <div className="border-t border-border pt-3">
              <div className="mb-2 text-xs uppercase tracking-wide text-text-muted">References</div>
              <ul className="flex flex-col gap-1.5">
                {REFS.map((r) => (
                  <li key={r} className="text-xs leading-relaxed text-text-secondary">{r}</li>
                ))}
              </ul>
            </div>
          </GlassCard>
        </div>
      </Reveal>

      <Notice>
        SHAP importances are served live from{" "}
        <span className="font-mono text-text-primary">turballoc.explain.shap_explainer</span> over a
        tractable surrogate fit on the same features as the forecast. All performance figures are
        walk-forward and net of costs — no look-ahead.
      </Notice>
    </div>
  );
}
