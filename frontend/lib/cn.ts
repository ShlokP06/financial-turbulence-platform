/** Tiny classname joiner — avoids a clsx dependency for our simple cases. */
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}
