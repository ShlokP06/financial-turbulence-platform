"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  /** Lift + glow slightly on hover. */
  interactive?: boolean;
}

export function GlassCard({ children, className, title, subtitle, action, interactive }: GlassCardProps) {
  const reduce = useReducedMotion();
  const hover = interactive && !reduce ? { y: -3, boxShadow: "var(--shadow-glow)" } : undefined;
  return (
    <motion.section
      whileHover={hover}
      transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
      className={cn("glass p-5 shadow-e1", className)}
    >
      {(title || action) && (
        <header className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title && <h3 className="text-sm font-semibold text-text-primary">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-text-muted">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      {children}
    </motion.section>
  );
}
