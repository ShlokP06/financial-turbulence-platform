"use client";

import { motion, useReducedMotion } from "framer-motion";

/** Semicircular gauge (0–1) with an emerald→amber→coral sweep. Used for regime risk. */
export function Gauge({ value, label }: { value: number; label?: string }) {
  const reduce = useReducedMotion();
  const v = Math.max(0, Math.min(1, value));
  const R = 80;
  const cx = 100;
  const cy = 100;
  const circumference = Math.PI * R; // semicircle
  const dash = circumference * v;

  const color = v < 0.4 ? "var(--pos)" : v < 0.7 ? "var(--warn)" : "var(--neg)";

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 116" className="w-full max-w-[280px]">
        <path
          d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none"
          stroke="var(--bg-3)"
          strokeWidth={14}
          strokeLinecap="round"
        />
        <motion.path
          d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth={14}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: reduce ? circumference - dash : circumference }}
          animate={{ strokeDashoffset: circumference - dash }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          style={{ filter: `drop-shadow(0 0 6px ${color})` }}
        />
        <text x={cx} y={cy - 6} textAnchor="middle" className="fill-text-primary" style={{ fontSize: 30, fontWeight: 600 }}>
          {(v * 100).toFixed(0)}%
        </text>
      </svg>
      {label && <span className="-mt-2 text-xs text-text-muted">{label}</span>}
    </div>
  );
}
