import { cn } from "@/lib/cn";

/** Shimmering placeholder while data loads. */
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-md bg-white/5",
        "after:absolute after:inset-0 after:-translate-x-full after:animate-shimmer",
        "after:bg-gradient-to-r after:from-transparent after:via-white/10 after:to-transparent",
        className,
      )}
    />
  );
}
