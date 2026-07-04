"use client";

interface SliderProps {
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
  "aria-label"?: string;
}

/** Range input styled to the emerald accent; fill tracks the current value. */
export function Slider({ value, min, max, step, onChange, ...rest }: SliderProps) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      aria-label={rest["aria-label"]}
      className="h-2 w-full cursor-pointer appearance-none rounded-full outline-none
        [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:appearance-none
        [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-accent
        [&::-webkit-slider-thumb]:shadow-[0_0_0_4px_var(--accent-muted)] [&::-webkit-slider-thumb]:transition-transform
        [&::-webkit-slider-thumb]:hover:scale-110
        [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:rounded-full
        [&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:bg-accent"
      style={{
        background: `linear-gradient(90deg, var(--accent) ${pct}%, var(--bg-3) ${pct}%)`,
      }}
    />
  );
}
