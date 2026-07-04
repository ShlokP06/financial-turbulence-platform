"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowUpRight } from "lucide-react";
import { BackendStatus } from "./BackendStatus";

const TITLES: Record<string, string> = {
  "/dashboard": "Overview",
  "/dashboard/turbulence": "Turbulence",
  "/dashboard/allocation": "Allocation",
  "/dashboard/stress": "Stress tests",
  "/dashboard/methodology": "Methodology",
};

export function Topbar() {
  const pathname = usePathname();
  const title = TITLES[pathname] ?? "Dashboard";
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-border bg-bg-deep/70 px-6 py-3 backdrop-blur-glass">
      <div>
        <span className="text-xs text-text-muted">Turballoc</span>
        <h2 className="text-lg font-semibold leading-tight tracking-tight">{title}</h2>
      </div>
      <div className="flex items-center gap-3">
        <BackendStatus />
        <Link
          href="/"
          className="hidden items-center gap-1 text-xs text-text-secondary hover:text-text-primary sm:flex"
        >
          Home <ArrowUpRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </header>
  );
}
