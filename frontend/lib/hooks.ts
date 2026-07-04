"use client";

import { useEffect, useState } from "react";
import type { ApiResult } from "./api";

interface AsyncState<T> {
  data: T | null;
  latencyMs: number | null;
  error: string | null;
  loading: boolean;
}

/** Run an api call on mount (and when `deps` change), tracking loading/error/latency. */
export function useApi<T>(fn: () => Promise<ApiResult<T>>, deps: unknown[] = []): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    latencyMs: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn()
      .then((res) => {
        if (alive) setState({ data: res.data, latencyMs: res.latencyMs, error: null, loading: false });
      })
      .catch((e) => {
        if (alive) setState((s) => ({ ...s, error: String(e), loading: false }));
      });
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}

/** Debounce a fast-changing value (e.g. a slider) so we don't refetch on every tick. */
export function useDebounced<T>(value: T, ms = 250): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), ms);
    return () => clearTimeout(id);
  }, [value, ms]);
  return debounced;
}
