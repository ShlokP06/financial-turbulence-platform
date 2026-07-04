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
import type { FeatureImportance } from "@/lib/types";
import { AXIS, GRID, GlassTooltip, PALETTE } from "./theme";

/** Horizontal SHAP importance bars. */
export function FeatureImportanceBar({ data }: { data: FeatureImportance[] }) {
  const rows = [...data].sort((a, b) => a.importance - b.importance);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart layout="vertical" data={rows} margin={{ top: 4, right: 16, bottom: 4, left: 8 }}>
        <CartesianGrid stroke={GRID} horizontal={false} />
        <XAxis type="number" tick={AXIS} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="feature" tick={{ ...AXIS, fontSize: 10 }} tickLine={false} axisLine={false} width={90} />
        <Tooltip content={<GlassTooltip formatter={(v) => v.toFixed(3)} />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
        <Bar dataKey="importance" name="mean |SHAP|" fill={PALETTE.accent} radius={[0, 3, 3, 0]} isAnimationActive animationDuration={700} />
      </BarChart>
    </ResponsiveContainer>
  );
}
