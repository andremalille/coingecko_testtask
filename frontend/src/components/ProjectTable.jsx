import React from "react";
import { formatUsd } from "../utils/format.js";

/**
 * Table of cryptocurrency projects.
 */
export default function ProjectTable({ projects }) {
  if (projects.length === 0) {
    return <p className="empty">No projects match the current filters.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Project</th>
          <th className="num">Market cap</th>
          <th className="num">FDV</th>
          <th className="num">24h volume</th>
          <th className="num">TVL</th>
        </tr>
      </thead>
      <tbody>
        {projects.map((p) => (
          <tr key={p.id}>
            <td>
              <span className="project">
                {p.image && <img src={p.image} alt="" width="20" height="20" />}
                <strong>{p.name}</strong>
                <span className="symbol">{p.symbol.toUpperCase()}</span>
              </span>
            </td>
            <td className="num">{formatUsd(p.market_cap)}</td>
            <td className="num">{formatUsd(p.fdv)}</td>
            <td className="num">{formatUsd(p.total_volume_24h)}</td>
            <td className="num">{formatUsd(p.tvl)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}