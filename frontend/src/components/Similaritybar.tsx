import type { CSSProperties } from "react";

interface SimilarityBarProps {
  value: number; // cosine similarity in the 0–1 range
}

function getColor(pct: number): string {
  if (pct >= 60) return "var(--color-text-success)";
  if (pct >= 40) return "var(--color-text-warning)";
  return "var(--color-text-danger)";
}

export function SimilarityBar({ value }: SimilarityBarProps) {
  const pct   = Math.round(value * 100);
  const color = getColor(pct);

  const trackStyle: CSSProperties = {
    flex:       1,
    height:     4,
    background: "var(--color-border-tertiary)",
    borderRadius: 2,
    overflow:   "hidden",
  };

  const fillStyle: CSSProperties = {
    width:      `${pct}%`,
    height:     "100%",
    background: color,
    borderRadius: 2,
    transition: "width 0.4s ease",
  };

  const labelStyle: CSSProperties = {
    fontSize:   11,
    color,
    minWidth:   32,
    textAlign:  "right",
  };

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={trackStyle}>
        <div style={fillStyle} />
      </div>
      <span style={labelStyle}>{pct}%</span>
    </div>
  );
}