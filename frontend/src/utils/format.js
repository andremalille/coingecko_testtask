/**
 * Formatting helpers for displaying money values.
 */

const usd = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 2,
});

/**
 * Format a number as compact USD, e.g. 12500000 -> "$12.5M".
 */
export function formatUsd(value) {
  return typeof value === "number" ? usd.format(value) : "–";
}
