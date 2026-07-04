"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AXIS, GRID, GlassTooltip, PALETTE } from "./theme";

/** Histogram of turbulence readings — shows the heavy right tail. */
export function TurbulenceDistribution({ values }: { values: number[] }) {
  const bins = 24;
  if (!values.length) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const width = (max - min) / bins || 1;
  const counts = new Array(bins).fill(0);
  for (const v of values) {
    const i = Math.min(bins - 1, Math.floor((v - min) / width));
    counts[i] += 1;
  }
  const data = counts.map((c, i) => ({ bin: (min + i * width).toFixed(1), count: c }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="bin" tick={AXIS} tickLine={false} axisLine={false} minTickGap={24} />
        <YAxis tick={AXIS} tickLine={false} axisLine={false} width={36} />
        <Tooltip content={<GlassTooltip formatter={(v) => `${v} days`} />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
        <Bar dataKey="count" name="Days" fill={PALETTE.accent} radius={[3, 3, 0, 0]} isAnimationActive animationDuration={700} />
      </BarChart>
    </ResponsiveContainer>
  );
}
