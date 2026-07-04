import type { Regime } from "@/lib/types";
import { regimeLabel } from "@/lib/format";
import { cn } from "@/lib/cn";

const styles: Record<Regime, string> = {
  calm: "border-regime-calm/40 bg-regime-calm/10 text-regime-calm",
  normal: "border-regime-normal/40 bg-regime-normal/10 text-regime-normal",
  elevated: "border-regime-elevated/40 bg-regime-elevated/10 text-regime-elevated",
  turbulent: "border-regime-turbulent/40 bg-regime-turbulent/10 text-regime-turbulent",
};

export function RegimeBadge({ regime, className }: { regime: Regime; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        styles[regime],
        className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {regimeLabel[regime]}
    </span>
  );
}
