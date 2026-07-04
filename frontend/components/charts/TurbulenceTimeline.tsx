"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TurbulencePoint } from "@/lib/types";
import { AXIS, GRID, GlassTooltip, PALETTE } from "./theme";

/** Turbulence over time with a stress-threshold reference line (90th percentile). */
export function TurbulenceTimeline({ data }: { data: TurbulencePoint[] }) {
  const values = data.map((d) => d.turbulence).sort((a, b) => a - b);
  const threshold = values.length ? values[Math.floor(values.length * 0.9)] : 0;
  const rows = data.map((d) => ({ date: d.date, turbulence: d.turbulence }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={rows} margin={{ top: 8, right: 8, bottom: 0, left: -8 }}>
        <defs>
          <linearGradient id="turbFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={PALETTE.accent} stopOpacity={0.35} />
            <stop offset="100%" stopColor={PALETTE.accent} stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis
          dataKey="date"
          tick={AXIS}
          tickLine={false}
          axisLine={false}
          minTickGap={48}
          tickFormatter={(v) => String(v).slice(0, 7)}
        />
        <YAxis tick={AXIS} tickLine={false} axisLine={false} width={40} />
        <ReferenceLine
          y={threshold}
          stroke={PALETTE.amber}
          strokeDasharray="4 4"
          label={{ value: "stress", fill: PALETTE.amber, fontSize: 10, position: "insideTopRight" }}
        />
        <Tooltip content={<GlassTooltip formatter={(v) => v.toFixed(2)} />} />
        <Area
          type="monotone"
          dataKey="turbulence"
          name="Turbulence"
          stroke={PALETTE.accent}
          strokeWidth={2}
          fill="url(#turbFill)"
          isAnimationActive
          animationDuration={900}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
