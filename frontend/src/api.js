/**
 * Backend API client. The frontend talks only to our own backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || "";

/**
 * Fetch the filtered project list from the backend.
 */
export async function fetchProjects({
  refresh = false,
  requirePreview = true,
} = {}) {
  const params = new URLSearchParams({
    refresh: String(refresh),
    require_preview: String(requirePreview),
  });
  const response = await fetch(`${API_BASE}/api/projects?${params}`);
  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      if (body.detail) detail = body.detail;
    } catch {
      // Response body was not JSON; keep the status text.
    }
    throw new Error(detail);
  }
  return response.json();
}
