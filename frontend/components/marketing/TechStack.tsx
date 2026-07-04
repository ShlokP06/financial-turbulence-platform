"use client";

import { Reveal } from "@/components/motion/Reveal";

const GROUPS = [
  { label: "Signals & models", items: ["Mahalanobis turbulence", "Ledoit–Wolf shrinkage", "Logistic exceedance", "TS-momentum"] },
  { label: "Allocation", items: ["Risk parity (ERC)", "Min-variance (SLSQP)", "Vol targeting", "Turbulence overlay"] },
  { label: "Backend", items: ["Python", "FastAPI", "DuckDB feature store", "scikit-learn", "pytest"] },
  { label: "Frontend", items: ["Next.js 15", "React 18", "Recharts", "Framer Motion", "Tailwind"] },
];

export function TechStack() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-20">
      <Reveal>
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">Built end to end</h2>
      </Reveal>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {GROUPS.map((g, i) => (
          <Reveal key={g.label} delay={i * 0.06}>
            <div className="glass h-full p-5 shadow-e1">
              <h3 className="mb-3 text-xs uppercase tracking-wide text-text-muted">{g.label}</h3>
              <ul className="flex flex-col gap-2">
                {g.items.map((it) => (
                  <li key={it} className="flex items-center gap-2 text-sm text-text-secondary">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent/70" />
                    {it}
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
