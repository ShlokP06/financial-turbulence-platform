"use client";

import { Sigma, Layers, Radar, XCircle } from "lucide-react";
import { EXCEEDANCE } from "@/lib/results";
import { Reveal } from "@/components/motion/Reveal";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

const CARDS = [
  {
    icon: Sigma,
    title: "Mahalanobis turbulence",
    body: "Hotelling's T² of daily returns against a trailing mean and covariance. High when assets move in jointly improbable ways — the statistical fingerprint of a regime break.",
  },
  {
    icon: Layers,
    title: "Estimation-robust allocation",
    body: "A Ledoit–Wolf-shrunk covariance drives minimum-variance / risk-parity weights. Dropping expected-return estimation removes the error-maximization that sinks mean-variance optimizers.",
  },
  {
    icon: Radar,
    title: "Exceedance forecasting",
    body: `Forecasting the turbulence level is a dead end (beaten by persistence). Forecasting exceedance — "will it breach a high threshold in ${EXCEEDANCE.horizonDays} days?" — is learnable: a regularized logistic model reaches AUC ${EXCEEDANCE.auc.toFixed(2)} vs ${EXCEEDANCE.persistenceAuc.toFixed(2)} for persistence.`,
  },
  {
    icon: XCircle,
    title: "What doesn't work (and why it's here)",
    body: "A deep LSTM-CNN level-forecaster was built, tested, and cut — it's indistinguishable from predicting the running mean. Reporting the negative result honestly is part of the method.",
    muted: true,
  },
];

export function Methodology() {
  return (
    <section id="method" className="mx-auto max-w-6xl px-6 py-20">
      <Reveal>
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">The method, honestly</h2>
        <p className="mt-2 max-w-2xl text-text-secondary">
          Grounded in published research — Kritzman &amp; Li (2010), Ledoit–Wolf shrinkage,
          Moskowitz–Ooi–Pedersen (2012) momentum — and validated without look-ahead.
        </p>
      </Reveal>

      <Stagger className="mt-10 grid gap-4 sm:grid-cols-2">
        {CARDS.map(({ icon: Icon, title, body, muted }) => (
          <StaggerItem key={title}>
            <div className={`glass h-full p-6 shadow-e1 ${muted ? "opacity-90" : ""}`}>
              <div className="mb-3 flex items-center gap-3">
                <span className={`flex h-9 w-9 items-center justify-center rounded-lg ${muted ? "bg-neg/12 text-neg" : "bg-accent/12 text-accent"}`}>
                  <Icon className="h-5 w-5" />
                </span>
                <h3 className="font-medium text-text-primary">{title}</h3>
              </div>
              <p className="text-sm leading-relaxed text-text-secondary">{body}</p>
            </div>
          </StaggerItem>
        ))}
      </Stagger>
    </section>
  );
}
