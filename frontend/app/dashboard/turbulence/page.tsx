"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/hooks";
import { GlassCard } from "@/components/ui/GlassCard";
import { Stat } from "@/components/ui/Stat";
import { Gauge } from "@/components/ui/Gauge";
import { Skeleton } from "@/components/ui/Skeleton";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { Reveal } from "@/components/motion/Reveal";
import { TurbulenceTimeline, TurbulenceDistribution } from "@/components/charts/dynamic";

function WhyCard({ date }: { date: string }) {
  const why = useApi(() => api.why(date), [date]);
  if (why.loading) return <Skeleton className="h-40" />;
  if (why.error || !why.data) {
    return (
      <p className="text-sm text-text-muted">
        Couldn&apos;t generate an explanation for that day.
      </p>
    );
  }
  const w = why.data;
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-2">
        {w.drivers.map((d) => (
          <span
            key={d.asset}
            className="rounded-md border border-border bg-white/[0.03] px-2 py-1 font-mono text-xs text-text-secondary"
          >
            {d.asset} {d.z >= 0 ? "+" : ""}
            {d.z.toFixed(1)}σ
          </span>
        ))}
      </div>
      <p className="text-sm leading-relaxed text-text-secondary">{w.explanation}</p>
      {w.sources.length > 0 && (
        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-text-muted">Sources</span>
          {w.sources.slice(0, 5).map((s) => (
            <a
              key={s.url}
              href={s.url}
              target="_blank"
              rel="noreferrer"
              className="truncate text-xs text-accent hover:underline"
            >
              {s.title}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

export default function TurbulencePage() {
  const history = useApi(() => api.turbulenceHistory(504));
  const risk = useApi(() => api.regimeRisk());
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  const series = history.data ?? [];
  const topDays = [...series].sort((a, b) => b.turbulence - a.turbulence).slice(0, 5);
  const values = series.map((p) => p.turbulence);
  const mean = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
  const peak = values.length ? Math.max(...values) : 0;
  const stressed = series.filter((p) => p.regime === "elevated" || p.regime === "turbulent").length;
  const stressedPct = series.length ? stressed / series.length : 0;

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <Reveal>
        <div className="grid gap-4 sm:grid-cols-3">
          <GlassCard>
            {history.loading ? <Skeleton className="h-14" /> : <Stat label="Mean" value={mean.toFixed(2)} sub="trailing window" />}
          </GlassCard>
          <GlassCard>
            {history.loading ? <Skeleton className="h-14" /> : <Stat label="Peak" value={peak.toFixed(2)} sub="max over window" />}
          </GlassCard>
          <GlassCard>
            {history.loading ? (
              <Skeleton className="h-14" />
            ) : (
              <Stat label="Time stressed" value={`${(stressedPct * 100).toFixed(0)}%`} sub="elevated or turbulent" />
            )}
          </GlassCard>
        </div>
      </Reveal>

      <Reveal delay={0.05}>
        <div className="grid gap-4 lg:grid-cols-3">
          <GlassCard
            title="Regime risk — leading de-risk signal"
            subtitle="P(turbulence breaches its high threshold within 10 days)"
          >
            {risk.loading ? (
              <Skeleton className="h-40" />
            ) : risk.data ? (
              <div className="flex flex-col items-center gap-2">
                <Gauge value={risk.data.probability} label={`as of ${risk.data.as_of}`} />
                <p className="text-center text-xs leading-relaxed text-text-muted">
                  Out-of-sample logistic exceedance model (AUC 0.71, beats persistence 0.69). This is the
                  trigger the allocation overlay consumes — not a level forecast.
                </p>
              </div>
            ) : (
              <p className="text-sm text-text-muted">
                Not enough history to score the exceedance model yet.
              </p>
            )}
          </GlassCard>

          <ChartFrame title="Turbulence over time" subtitle="Trailing ~2 years" className="lg:col-span-2" height={300}>
            {history.loading ? (
              <Skeleton className="h-full" />
            ) : series.length ? (
              <TurbulenceTimeline data={series} />
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-text-muted">
                Couldn&apos;t reach the backend.
              </div>
            )}
          </ChartFrame>
        </div>
      </Reveal>

      <Reveal delay={0.05}>
        <GlassCard title="Why was it turbulent?" subtitle="Driving asset moves — news narration when GROQ + Tavily keys are set">
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-text-muted">Pick a high-turbulence day:</span>
              {topDays.map((d) => (
                <button
                  key={d.date}
                  onClick={() => setSelectedDate(d.date)}
                  className={`rounded-md border px-2 py-1 font-mono text-xs transition-colors ${
                    selectedDate === d.date
                      ? "border-accent text-accent"
                      : "border-border text-text-secondary hover:border-accent/50"
                  }`}
                >
                  {d.date} · {d.turbulence.toFixed(1)}
                </button>
              ))}
            </div>
            {selectedDate ? (
              <WhyCard key={selectedDate} date={selectedDate} />
            ) : (
              <p className="text-sm text-text-muted">Select a day above to see why turbulence spiked.</p>
            )}
          </div>
        </GlassCard>
      </Reveal>

      <Reveal delay={0.05}>
        <ChartFrame title="Distribution" subtitle="How often each turbulence level occurs" height={260}>
          {history.loading ? (
            <Skeleton className="h-full" />
          ) : values.length ? (
            <TurbulenceDistribution values={values} />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-text-muted">No data.</div>
          )}
        </ChartFrame>
      </Reveal>
    </div>
  );
}
