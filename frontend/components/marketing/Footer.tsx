import Link from "next/link";
import { Activity, ArrowRight } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto max-w-6xl px-6 py-14">
        <div className="glass flex flex-col items-start justify-between gap-6 p-8 shadow-e1 sm:flex-row sm:items-center">
          <div>
            <h3 className="text-xl font-semibold tracking-tight">Explore the live signal</h3>
            <p className="mt-1 text-sm text-text-secondary">
              Drag the risk dial, inspect crisis behavior, and see today&apos;s regime.
            </p>
          </div>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-3 text-sm font-medium text-bg-deep shadow-[0_10px_40px_-10px_var(--accent-glow)] transition-all hover:-translate-y-0.5 hover:bg-accent-soft"
          >
            Open dashboard <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-3 text-xs text-text-muted sm:flex-row">
          <span className="flex items-center gap-2">
            <Activity className="h-3.5 w-3.5 text-accent" /> Turballoc — turbulence-managed allocation
          </span>
          <span>Research demo · walk-forward, net of costs · not investment advice</span>
        </div>
      </div>
    </footer>
  );
}
