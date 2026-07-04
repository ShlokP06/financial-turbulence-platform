"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, LayoutDashboard, PieChart, ShieldAlert, Waves, FlaskConical } from "lucide-react";
import { cn } from "@/lib/cn";

const NAV = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/turbulence", label: "Turbulence", icon: Waves },
  { href: "/dashboard/allocation", label: "Allocation", icon: PieChart },
  { href: "/dashboard/stress", label: "Stress tests", icon: ShieldAlert },
  { href: "/dashboard/methodology", label: "Methodology", icon: FlaskConical },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-60 shrink-0 flex-col gap-1 border-r border-border p-4 lg:flex">
      <Link href="/" className="mb-6 flex items-center gap-2 px-2">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15 text-accent">
          <Activity className="h-4 w-4" />
        </span>
        <span className="font-semibold tracking-tight">Turballoc</span>
      </Link>
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = pathname === href;
        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors duration-base ease-standard",
              active
                ? "bg-accent/10 text-accent"
                : "text-text-secondary hover:bg-white/[0.03] hover:text-text-primary",
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        );
      })}
      <div className="mt-auto px-3 pt-6 text-xs text-text-muted">
        Kritzman &amp; Li (2010) turbulence · leak-safe walk-forward
      </div>
    </aside>
  );
}
