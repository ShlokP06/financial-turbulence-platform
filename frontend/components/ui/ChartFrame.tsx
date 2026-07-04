import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface ChartFrameProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  height?: number;
  className?: string;
  children: ReactNode;
}

/** Glass panel wrapping a chart, with a titled header and fixed plot height. */
export function ChartFrame({ title, subtitle, action, height = 300, className, children }: ChartFrameProps) {
  return (
    <section className={cn("glass p-5 shadow-e1", className)}>
      <header className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
          {subtitle && <p className="mt-0.5 text-xs text-text-muted">{subtitle}</p>}
        </div>
        {action}
      </header>
      <div style={{ height }}>{children}</div>
    </section>
  );
}
