"use client";

import { animate, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { cn } from "@/lib/cn";

/** Count-up number that eases from 0 to `value` on mount. */
export function CountUp({
  value,
  digits = 2,
  prefix = "",
  suffix = "",
  className,
}: {
  value: number;
  digits?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
}) {
  const reduce = useReducedMotion();
  const [display, setDisplay] = useState(reduce ? value : 0);
  const ref = useRef(value);

  useEffect(() => {
    if (reduce) {
      setDisplay(value);
      return;
    }
    const controls = animate(ref.current, value, {
      duration: 0.9,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => setDisplay(v),
    });
    ref.current = value;
    return () => controls.stop();
  }, [value, reduce]);

  return (
    <span className={cn("tabular", className)}>
      {prefix}
      {display.toFixed(digits)}
      {suffix}
    </span>
  );
}

interface StatProps {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  tone?: "default" | "pos" | "neg" | "accent";
}

const toneClass: Record<NonNullable<StatProps["tone"]>, string> = {
  default: "text-text-primary",
  pos: "text-pos",
  neg: "text-neg",
  accent: "text-accent",
};

export function Stat({ label, value, sub, tone = "default" }: StatProps) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs font-medium uppercase tracking-wide text-text-muted">{label}</span>
      <span className={cn("text-2xl font-semibold leading-none", toneClass[tone])}>{value}</span>
      {sub && <span className="text-xs text-text-secondary">{sub}</span>}
    </div>
  );
}
