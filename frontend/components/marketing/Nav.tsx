"use client";

import Link from "next/link";
import { Activity } from "lucide-react";

export function Nav() {
  return (
    <nav className="sticky top-0 z-40 border-b border-border bg-bg-deep/60 backdrop-blur-glass">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15 text-accent">
            <Activity className="h-4 w-4" />
          </span>
          <span className="font-semibold tracking-tight">Turballoc</span>
        </Link>
        <div className="hidden items-center gap-7 text-sm text-text-secondary sm:flex">
          <a href="#how" className="hover:text-text-primary">How it works</a>
          <a href="#results" className="hover:text-text-primary">Results</a>
          <a href="#method" className="hover:text-text-primary">Method</a>
        </div>
        <Link
          href="/dashboard"
          className="rounded-lg bg-accent px-3.5 py-2 text-sm font-medium text-bg-deep shadow-[0_8px_30px_-8px_var(--accent-glow)] transition-all hover:-translate-y-0.5 hover:bg-accent-soft"
        >
          Open dashboard
        </Link>
      </div>
    </nav>
  );
}
