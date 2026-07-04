"use client";

import { Database, Waves, Scale, Gauge, ShieldHalf, TrendingUp, ArrowRight } from "lucide-react";
import { Reveal } from "@/components/motion/Reveal";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

const STEPS = [
  { icon: Database, title: "Ingest", body: "Daily prices for a multi-asset ETF universe + a credit-stress proxy." },
  { icon: Waves, title: "Turbulence signal", body: "Mahalanobis distance of returns from a trailing mean/covariance (Ledoit–Wolf shrunk)." },
  { icon: Scale, title: "Risk-parity base", body: "Minimum-variance / equal-risk weights — no fragile return estimates." },
  { icon: Gauge, title: "Vol target", body: "Scale gross exposure to a constant annualized volatility." },
  { icon: ShieldHalf, title: "Turbulence overlay", body: "De-risk into cash as turbulence crosses a rolling threshold." },
  { icon: TrendingUp, title: "Momentum tilt", body: "Time-series momentum nudges winners up, losers down." },
];

export function Pipeline() {
  return (
    <section id="how" className="mx-auto max-w-6xl px-6 py-20">
      <Reveal>
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">How a single rebalance is decided</h2>
        <p className="mt-2 max-w-2xl text-text-secondary">
          Every step is causal and computed only from information available on the day — the same
          pipeline runs live in the dashboard and inside the leak-safe backtest.
        </p>
      </Reveal>

      <Stagger className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {STEPS.map(({ icon: Icon, title, body }, i) => (
          <StaggerItem key={title}>
            <div className="glass h-full p-5 shadow-e1">
              <div className="mb-3 flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/12 text-accent">
                  <Icon className="h-5 w-5" />
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-xs tabular text-text-muted">{String(i + 1).padStart(2, "0")}</span>
                  <h3 className="font-medium text-text-primary">{title}</h3>
                </div>
              </div>
              <p className="text-sm leading-relaxed text-text-secondary">{body}</p>
            </div>
          </StaggerItem>
        ))}
      </Stagger>

      <Reveal delay={0.1}>
        <div className="mt-6 flex flex-wrap items-center gap-2 text-xs text-text-muted">
          <span className="rounded-md border border-border px-2 py-1">weights</span>
          <ArrowRight className="h-3.5 w-3.5" />
          <span className="rounded-md border border-border px-2 py-1">apply cost + drift</span>
          <ArrowRight className="h-3.5 w-3.5" />
          <span className="rounded-md border border-border px-2 py-1">next rebalance in 21d</span>
        </div>
      </Reveal>
    </section>
  );
}
