"use client";

import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useApi } from "@/lib/hooks";
import { RESEARCH_BEST, PERIOD, COST_BPS } from "@/lib/results";
import { pct } from "@/lib/format";
import { HeroSparkline } from "@/components/charts/dynamic";
import { RegimeBadge } from "@/components/ui/RegimeBadge";
import { CountUp } from "@/components/ui/Stat";

export function Hero() {
  const latest = useApi(() => api.latestTurbulence());
  const history = useApi(() => api.turbulenceHistory(252));

  return (
    <section className="relative mx-auto max-w-6xl px-6 pb-16 pt-16 sm:pt-24">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col items-start gap-6"
      >
        <span className="inline-flex items-center gap-2 rounded-full border border-border bg-white/[0.03] px-3 py-1 text-xs text-text-secondary">
          <ShieldCheck className="h-3.5 w-3.5 text-accent" />
          Kritzman–Li turbulence · risk-parity · leak-safe walk-forward
        </span>

        <h1 className="max-w-3xl text-4xl font-semibold leading-[1.08] tracking-tight sm:text-6xl">
          A turbulence index that{" "}
          <span className="bg-gradient-to-r from-accent to-accent-soft bg-clip-text text-transparent">
            scales portfolio risk
          </span>
          , not a return forecaster.
        </h1>

        <p className="max-w-2xl text-lg leading-relaxed text-text-secondary">
          Turballoc measures how statistically abnormal today&apos;s cross-asset moves are, then
          continuously dials portfolio exposure up or down — holding cash when markets dislocate.
          A minimum-variance base, volatility targeting, and a turbulence overlay, proven on{" "}
          {PERIOD} data net of {COST_BPS} bps.
        </p>

        <div className="flex flex-wrap items-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-3 text-sm font-medium text-bg-deep shadow-[0_10px_40px_-10px_var(--accent-glow)] transition-all hover:-translate-y-0.5 hover:bg-accent-soft"
          >
            Explore the live dashboard <ArrowRight className="h-4 w-4" />
          </Link>
          <a
            href="#results"
            className="inline-flex items-center gap-2 rounded-lg border border-border px-5 py-3 text-sm font-medium text-text-secondary transition-colors hover:border-border-strong hover:text-text-primary"
          >
            See the numbers
          </a>
        </div>
      </motion.div>

      {/* Live signal card */}
      <motion.div
        initial={{ opacity: 0, y: 26 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        className="glass mt-12 grid gap-6 p-6 shadow-e2 sm:grid-cols-[1.1fr_1fr]"
      >
        <div className="flex flex-col justify-between gap-4">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-wide text-text-muted">Live turbulence signal</span>
            {latest.data ? <RegimeBadge regime={latest.data.regime} /> : null}
          </div>
          <div>
            <div className="text-5xl font-semibold tabular">
              {latest.data ? <CountUp value={latest.data.turbulence} digits={1} /> : "—"}
            </div>
            <div className="mt-1 text-xs text-text-muted">
              {latest.data ? `Mahalanobis distance · as of ${latest.data.date}` : "connecting to backend…"}
            </div>
          </div>
          <div className="h-16">
            {history.data ? <HeroSparkline data={history.data} /> : null}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 border-t border-border pt-5 sm:border-l sm:border-t-0 sm:pl-6 sm:pt-0">
          <HeroMetric label="Sharpe" value={RESEARCH_BEST.sharpe.toFixed(2)} tone="accent" />
          <HeroMetric label="Sortino" value={RESEARCH_BEST.sortino.toFixed(2)} tone="accent" />
          <HeroMetric label="Annualized vol" value={pct(RESEARCH_BEST.annVol, 1)} />
          <HeroMetric label="Max drawdown" value={pct(RESEARCH_BEST.maxDrawdown, 1)} tone="pos" />
          <p className="col-span-2 text-[11px] leading-relaxed text-text-muted">
            Served live — expanded 14-asset universe with a time-series momentum tilt, leak-safe
            walk-forward and net of costs.
          </p>
        </div>
      </motion.div>
    </section>
  );
}

function HeroMetric({ label, value, tone }: { label: string; value: string; tone?: "accent" | "pos" }) {
  const c = tone === "accent" ? "text-accent" : tone === "pos" ? "text-pos" : "text-text-primary";
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-text-muted">{label}</div>
      <div className={`mt-1 text-2xl font-semibold tabular ${c}`}>{value}</div>
    </div>
  );
}
