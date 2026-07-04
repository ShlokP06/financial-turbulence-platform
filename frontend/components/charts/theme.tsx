"use client";

import type { ReactNode } from "react";

export const AXIS = { stroke: "var(--text-muted)", fontSize: 11 };
export const GRID = "rgba(255,255,255,0.06)";

export const PALETTE = {
  accent: "#10b981",
  accentSoft: "#34d399",
  blue: "#38bdf8",
  amber: "#f59e0b",
  coral: "#ef5350",
  muted: "#6b7681",
};

/** Shared dark glass tooltip. */
export function GlassTooltip({
  active,
  payload,
  label,
  formatter,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string | number;
  formatter?: (value: number, name: string) => ReactNode;
}) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="glass glass-strong rounded-lg px-3 py-2 text-xs shadow-e2">
      {label !== undefined && <div className="mb-1 font-medium text-text-primary">{label}</div>}
      <div className="flex flex-col gap-1">
        {payload.map((p, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full" style={{ background: p.color }} />
            <span className="text-text-secondary">{p.name}</span>
            <span className="tabular ml-auto font-medium text-text-primary">
              {formatter ? formatter(p.value, p.name) : p.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
