import React, { useCallback, useEffect, useMemo, useState } from "react";
import { fetchProjects } from "./api.js";
import Filters from "./components/Filters.jsx";
import ProjectTable from "./components/ProjectTable.jsx";
import { applyFilters } from "./utils/filterSort.js";

const INITIAL_FILTERS = { search: "", maxFdv: "", sortField: "market_cap", sortDir: "desc" };

/**
 * Root component: loads projects from the backend and renders the screener.
 */
export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(INITIAL_FILTERS);
  const [requirePreview, setRequirePreview] = useState(true);

  /** Load (or reload) projects from the backend. */
  const load = useCallback(
    async (refresh = false) => {
      setLoading(true);
      setError(null);
      try {
        setData(await fetchProjects({ refresh, requirePreview }));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [requirePreview]
  );

  useEffect(() => {
    load();
  }, [load]);

  const visible = useMemo(
    () => (data ? applyFilters(data.projects, filters) : []),
    [data, filters]
  );

  return (
    <main>
      <header>
        <h1>Crypto Screener</h1>
        <button onClick={() => load(true)} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </button>
      </header>

      <label className="strict">
        <input
          type="checkbox"
          checked={requirePreview}
          onChange={(e) => setRequirePreview(e.target.checked)}
        />
        Only coins with preview_listing = true (untick to see all other matches)
      </label>

      <Filters values={filters} onChange={(patch) => setFilters((f) => ({ ...f, ...patch }))} />

      {error && <p className="error">Failed to load data: {error}</p>}
      {loading && !data && (
        <p>Loading projects. The first request can take several minutes on the free API plan.</p>
      )}

      {data && (
        <>
          <p className="meta">
            Showing {visible.length} of {data.count} projects · updated{" "}
            {new Date(data.generated_at).toLocaleTimeString()}
          </p>
          <ProjectTable projects={visible} />
        </>
      )}
    </main>
  );
}