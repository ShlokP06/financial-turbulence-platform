"use client";

import dynamic from "next/dynamic";
import { Skeleton } from "@/components/ui/Skeleton";

const loading = () => <Skeleton className="h-full w-full" />;

/** Recharts pulls in browser-only APIs — load every chart client-side to avoid SSR/hydration cost. */
export const TurbulenceTimeline = dynamic(
  () => import("./TurbulenceTimeline").then((m) => m.TurbulenceTimeline),
  { ssr: false, loading },
);
export const TurbulenceDistribution = dynamic(
  () => import("./TurbulenceDistribution").then((m) => m.TurbulenceDistribution),
  { ssr: false, loading },
);
export const WeightsDonut = dynamic(() => import("./WeightsDonut").then((m) => m.WeightsDonut), {
  ssr: false,
  loading,
});
export const EquityCurve = dynamic(() => import("./EquityCurve").then((m) => m.EquityCurve), {
  ssr: false,
  loading,
});
export const CrisisBars = dynamic(() => import("./CrisisBars").then((m) => m.CrisisBars), {
  ssr: false,
  loading,
});
export const FeatureImportanceBar = dynamic(
  () => import("./FeatureImportanceBar").then((m) => m.FeatureImportanceBar),
  { ssr: false, loading },
);
export const HeroSparkline = dynamic(() => import("./HeroSparkline").then((m) => m.HeroSparkline), {
  ssr: false,
  loading,
});
