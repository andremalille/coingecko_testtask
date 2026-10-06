/**
 * Pure helpers for client-side filtering, searching and sorting.
 */

/** Supported sort fields mapped to the project property they use. */
export const SORT_FIELDS = {
  market_cap: "market_cap",
  volume: "total_volume_24h",
};

/**
 * Apply FDV filter, name search and sorting to a project list.
 */
export function applyFilters(projects, { search, maxFdv, sortField, sortDir }) {
  const query = search.trim().toLowerCase();
  const limit = maxFdv === "" ? null : Number(maxFdv);
  const key = SORT_FIELDS[sortField];
  const direction = sortDir === "asc" ? 1 : -1;

  return projects
    .filter((p) => {
      if (
        query &&
        !p.name.toLowerCase().includes(query) &&
        !p.symbol.toLowerCase().includes(query)
      ) {
        return false;
      }
      if (limit !== null && !Number.isNaN(limit) && p.fdv >= limit) {
        return false;
      }
      return true;
    })
    .sort((a, b) => (a[key] - b[key]) * direction);
}
