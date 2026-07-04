import Link from "next/link";
import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface ButtonProps {
  href: string;
  children: ReactNode;
  variant?: "primary" | "ghost";
  className?: string;
}

/** Link-styled CTA. Primary carries the accent glow. */
export function Button({ href, children, variant = "primary", className }: ButtonProps) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-base ease-standard";
  const styles =
    variant === "primary"
      ? "bg-accent text-bg-deep shadow-[0_8px_30px_-8px_var(--accent-glow)] hover:bg-accent-soft hover:-translate-y-0.5"
      : "border border-border text-text-secondary hover:border-border-strong hover:text-text-primary";
  return (
    <Link href={href} className={cn(base, styles, className)}>
      {children}
    </Link>
  );
}
