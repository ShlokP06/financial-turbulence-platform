import type { Regime } from "./types";

export function pct(x: number, digits = 1): string {
  return `${(x * 100).toFixed(digits)}%`;
}

export function num(x: number, digits = 2): string {
  return x.toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function shortDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export const regimeLabel: Record<Regime, string> = {
  calm: "Calm",
  normal: "Normal",
  elevated: "Elevated",
  turbulent: "Turbulent",
};

export const regimeColorVar: Record<Regime, string> = {
  calm: "var(--regime-calm)",
  normal: "var(--regime-normal)",
  elevated: "var(--regime-elevated)",
  turbulent: "var(--regime-turbulent)",
};
