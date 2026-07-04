"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { GlassTooltip } from "./theme";

const COLORS = [
  "#10b981", "#34d399", "#38bdf8", "#818cf8", "#f59e0b",
  "#fb923c", "#f472b6", "#a78bfa", "#22d3ee", "#facc15",
  "#4ade80", "#60a5fa", "#f87171", "#c084fc",
];

/** Allocation weights as a donut. CASH is rendered muted. */
export function WeightsDonut({ weights }: { weights: Record<string, number> }) {
  const data = Object.entries(weights)
    .filter(([, w]) => w > 0.0005)
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({ name, value }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius="58%"
          outerRadius="82%"
          paddingAngle={2}
          stroke="none"
          isAnimationActive
          animationDuration={800}
        >
          {data.map((d, i) => (
            <Cell key={d.name} fill={d.name === "CASH" ? "#4b5563" : COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<GlassTooltip formatter={(v) => `${(v * 100).toFixed(1)}%`} />} />
      </PieChart>
    </ResponsiveContainer>
  );
}
