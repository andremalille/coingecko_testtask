import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Vite configuration.
 * In development, requests to /api are proxied to the FastAPI backend so the
 * browser only ever talks to our own origin.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
