/** Fixed ambient emerald blobs behind all content — the cinematic glass backdrop.
    Pure CSS animation (animate-blob-drift); disabled under prefers-reduced-motion via globals. */
export function AmbientBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-bg-deep" />
      <div
        className="absolute -left-40 -top-40 h-[520px] w-[520px] rounded-full animate-blob-drift"
        style={{ background: "radial-gradient(circle, rgba(16,185,129,0.14), transparent 62%)", filter: "blur(40px)" }}
      />
      <div
        className="absolute right-[-10rem] top-1/4 h-[460px] w-[460px] rounded-full animate-blob-drift"
        style={{ background: "radial-gradient(circle, rgba(56,189,248,0.10), transparent 62%)", filter: "blur(50px)", animationDelay: "-8s" }}
      />
      <div
        className="absolute bottom-[-12rem] left-1/3 h-[500px] w-[500px] rounded-full animate-blob-drift"
        style={{ background: "radial-gradient(circle, rgba(16,185,129,0.08), transparent 60%)", filter: "blur(60px)", animationDelay: "-15s" }}
      />
      {/* faint grid texture */}
      <div
        className="absolute inset-0 opacity-[0.15]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse at center, black, transparent 75%)",
        }}
      />
    </div>
  );
}
