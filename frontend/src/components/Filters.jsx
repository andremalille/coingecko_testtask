import React from "react";

/**
 * Controls for search, FDV limit and sorting.
 */
export default function Filters({ values, onChange }) {
  return (
    <div className="filters">
      <label>
        Search by name
        <input
          type="search"
          placeholder="e.g. eth"
          value={values.search}
          onChange={(e) => onChange({ search: e.target.value })}
        />
      </label>

      <label>
        Max FDV (USD)
        <input
          type="number"
          min="0"
          placeholder="e.g. 50000000"
          value={values.maxFdv}
          onChange={(e) => onChange({ maxFdv: e.target.value })}
        />
      </label>

      <label>
        Sort by
        <select value={values.sortField} onChange={(e) => onChange({ sortField: e.target.value })}>
          <option value="market_cap">Market cap</option>
          <option value="volume">24h volume</option>
        </select>
      </label>

      <label>
        Direction
        <select value={values.sortDir} onChange={(e) => onChange({ sortDir: e.target.value })}>
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </label>
    </div>
  );
}