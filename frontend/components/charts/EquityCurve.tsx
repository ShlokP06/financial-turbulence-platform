"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EquityPoint } from "@/lib/types";
import { AXIS, GRID, GlassTooltip, PALETTE } from "./theme";

/** Growth-of-$1 equity curves: strategy vs benchmark. */
export function EquityCurve({ data }: { data: EquityPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -8 }}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis
          dataKey="date"
          tick={AXIS}
          tickLine={false}
          axisLine={false}
          minTickGap={56}
          tickFormatter={(v) => String(v).slice(0, 4)}
        />
        <YAxis tick={AXIS} tickLine={false} axisLine={false} width={40} tickFormatter={(v) => `${v}×`} />
        <Tooltip content={<GlassTooltip formatter={(v) => `${v.toFixed(2)}×`} />} />
        <Line
          type="monotone"
          dataKey="strategy"
          name="Turbulence-managed"
          stroke={PALETTE.accent}
          strokeWidth={2}
          dot={false}
          isAnimationActive
          animationDuration={900}
        />
        <Line
          type="monotone"
          dataKey="benchmark"
          name="Equal-weight"
          stroke={PALETTE.muted}
          strokeWidth={1.5}
          strokeDasharray="5 4"
          dot={false}
          isAnimationActive
          animationDuration={900}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
