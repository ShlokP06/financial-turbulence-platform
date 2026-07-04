"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { CrisisRow } from "@/lib/results";
import { AXIS, GRID, GlassTooltip, PALETTE } from "./theme";

/** Grouped bars comparing crisis-window total return: SPY vs EW vs strategy. */
export function CrisisBars({ data }: { data: CrisisRow[] }) {
  const rows = data.map((d) => ({
    window: d.window,
    SPY: +(d.spy * 100).toFixed(1),
    "Equal-weight": +(d.equalWeight * 100).toFixed(1),
    Strategy: +(d.strategyMomentum * 100).toFixed(1),
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={rows} margin={{ top: 8, right: 8, bottom: 0, left: -8 }} barGap={2}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="window" tick={{ ...AXIS, fontSize: 10 }} tickLine={false} axisLine={false} interval={0} angle={-12} textAnchor="end" height={60} />
        <YAxis tick={AXIS} tickLine={false} axisLine={false} width={40} tickFormatter={(v) => `${v}%`} />
        <Tooltip content={<GlassTooltip formatter={(v) => `${v.toFixed(1)}%`} />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="SPY" fill={PALETTE.coral} radius={[3, 3, 0, 0]} isAnimationActive animationDuration={700} />
        <Bar dataKey="Equal-weight" fill={PALETTE.amber} radius={[3, 3, 0, 0]} isAnimationActive animationDuration={700} />
        <Bar dataKey="Strategy" fill={PALETTE.accent} radius={[3, 3, 0, 0]} isAnimationActive animationDuration={700} />
      </BarChart>
    </ResponsiveContainer>
  );
}
