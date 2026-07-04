"use client";

import { api } from "@/lib/api";
import { useApi } from "@/lib/hooks";
import type { Regime } from "@/lib/types";
import { GlassCard } from "@/components/ui/GlassCard";
import { Stat, CountUp } from "@/components/ui/Stat";
import { Skeleton } from "@/components/ui/Skeleton";
import { RegimeBadge } from "@/components/ui/RegimeBadge";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { Reveal } from "@/components/motion/Reveal";
import { TurbulenceTimeline, WeightsDonut } from "@/components/charts/dynamic";

const posture: Record<Regime, string> = {
  calm: "Risk-on",
  normal: "Balanced",
  elevated: "Defensive",
  turbulent: "Risk-off",
};

export default function Overview() {
  const latest = useApi(() => api.latestTurbulence());
  const history = useApi(() => api.turbulenceHistory(504));
  const weights = useApi(() => api.weights());
  const risk = useApi(() => api.regimeRisk());

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <Reveal>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <GlassCard>
            {latest.loading ? (
              <Skeleton className="h-14" />
            ) : (
              <Stat
                label="Turbulence"
                value={latest.data ? <CountUp value={latest.data.turbulence} digits={1} /> : "—"}
                sub="Mahalanobis distance"
              />
            )}
          </GlassCard>
          <GlassCard>
            {latest.loading ? (
              <Skeleton className="h-14" />
            ) : (
              <Stat
                label="Regime"
                value={latest.data ? <RegimeBadge regime={latest.data.regime} /> : "—"}
                sub={latest.data ? `as of ${latest.data.date}` : undefined}
              />
            )}
          </GlassCard>
          <GlassCard>
            {latest.loading ? (
              <Skeleton className="h-14" />
            ) : (
              <Stat
                label="Risk posture"
                value={latest.data ? posture[latest.data.regime] : "—"}
                sub="min-variance · vol-targeted"
                tone="accent"
              />
            )}
          </GlassCard>
          <GlassCard>
            {risk.loading ? (
              <Skeleton className="h-14" />
            ) : (
              <Stat
                label="Regime risk (10d)"
                value={
                  risk.data ? (
                    <CountUp value={risk.data.probability * 100} digits={0} suffix="%" />
                  ) : (
                    "—"
                  )
                }
                sub={risk.data ? "P(turbulence breach)" : "insufficient history"}
                tone={risk.data && risk.data.probability > 0.6 ? "neg" : "default"}
              />
            )}
          </GlassCard>
        </div>
      </Reveal>

      <Reveal delay={0.05}>
        <div className="grid gap-4 lg:grid-cols-3">
          <ChartFrame
            title="Turbulence"
            subtitle="Trailing ~2 years"
            className="lg:col-span-2"
            height={300}
            action={
              latest.latencyMs !== null ? (
                <span className="tabular text-xs text-text-muted">{latest.latencyMs.toFixed(1)} ms</span>
              ) : null
            }
          >
            {history.loading ? (
              <Skeleton className="h-full" />
            ) : history.data && history.data.length ? (
              <TurbulenceTimeline data={history.data} />
            ) : (
              <Empty error={history.error} />
            )}
          </ChartFrame>

          <ChartFrame title="Allocation" subtitle="Recommended weights" height={300}>
            {weights.loading ? (
              <Skeleton className="h-full" />
            ) : weights.data ? (
              <WeightsDonut weights={weights.data.weights} />
            ) : (
              <Empty error={weights.error} />
            )}
          </ChartFrame>
        </div>
      </Reveal>
    </div>
  );
}

function Empty({ error }: { error: string | null }) {
  return (
    <div className="flex h-full items-center justify-center text-center text-sm text-text-muted">
      {error ? "Couldn't reach the backend — is it running on :8000?" : "No data."}
    </div>
  );
}
