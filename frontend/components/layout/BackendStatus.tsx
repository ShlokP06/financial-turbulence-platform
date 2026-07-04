"use client";

import { api } from "@/lib/api";
import { useApi } from "@/lib/hooks";

/** Live backend health pill with round-trip latency. */
export function BackendStatus() {
  const health = useApi(() => api.health());
  const ok = !!health.data && !health.error;
  const color = health.loading ? "bg-text-muted" : ok ? "bg-pos" : "bg-neg";
  const label = health.loading ? "Connecting" : ok ? "Backend live" : "Backend offline";

  return (
    <div className="flex items-center gap-2 rounded-full border border-border bg-white/[0.02] px-3 py-1.5 text-xs">
      <span className={`relative flex h-2 w-2`}>
        {ok && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-pos opacity-60" />}
        <span className={`relative inline-flex h-2 w-2 rounded-full ${color}`} />
      </span>
      <span className="text-text-secondary">{label}</span>
      {health.latencyMs !== null && (
        <span className="tabular text-text-muted">· {health.latencyMs.toFixed(0)} ms</span>
      )}
    </div>
  );
}
