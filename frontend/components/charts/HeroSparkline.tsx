"use client";

import { Area, AreaChart, ResponsiveContainer } from "recharts";
import type { TurbulencePoint } from "@/lib/types";
import { PALETTE } from "./theme";

/** Minimal turbulence sparkline for the hero. */
export function HeroSparkline({ data }: { data: TurbulencePoint[] }) {
  const rows = data.map((d) => ({ v: d.turbulence }));
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={rows} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={PALETTE.accent} stopOpacity={0.4} />
            <stop offset="100%" stopColor={PALETTE.accent} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area type="monotone" dataKey="v" stroke={PALETTE.accent} strokeWidth={1.5} fill="url(#sparkFill)" isAnimationActive animationDuration={1100} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
