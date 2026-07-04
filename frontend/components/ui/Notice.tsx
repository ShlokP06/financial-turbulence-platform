import type { ReactNode } from "react";
import { Info } from "lucide-react";
import { cn } from "@/lib/cn";

/** Inline informational callout — used to label assumptions and data provenance honestly. */
export function Notice({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        "flex items-start gap-2.5 rounded-lg border border-border bg-white/[0.02] px-4 py-3 text-sm text-text-secondary",
        className,
      )}
    >
      <Info className="mt-0.5 h-4 w-4 shrink-0 text-accent" aria-hidden />
      <div className="leading-relaxed">{children}</div>
    </div>
  );
}
