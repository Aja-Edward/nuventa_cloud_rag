import { useState } from "react";
import type { CSSProperties } from "react";
import { SimilarityBar } from "./Similaritybar";
import type { SourceChunk } from "../types/types";

interface SourceCardProps {
  source: SourceChunk;
  index:  number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  const [open, setOpen] = useState<boolean>(false);

  const filename = source.source.split(/[\\/]/).pop() ?? source.source;

  const wrapperStyle: CSSProperties = {
    border:       "0.5px solid var(--color-border-tertiary)",
    borderRadius: "var(--border-radius-md)",
    overflow:     "hidden",
    marginBottom: 6,
  };

  const headerBtnStyle: CSSProperties = {
    width:      "100%",
    background: "var(--color-background-secondary)",
    border:     "none",
    padding:    "8px 12px",
    display:    "flex",
    alignItems: "center",
    gap:        8,
    cursor:     "pointer",
    textAlign:  "left",
  };

  const badgeStyle: CSSProperties = {
    fontSize:     11,
    fontWeight:   500,
    background:   "var(--color-background-info)",
    color:        "var(--color-text-info)",
    borderRadius: 4,
    padding:      "2px 6px",
    flexShrink:   0,
  };

  const filenameStyle: CSSProperties = {
    fontSize:     12,
    color:        "var(--color-text-secondary)",
    flex:         1,
    overflow:     "hidden",
    textOverflow: "ellipsis",
    whiteSpace:   "nowrap",
  };

  const chevronStyle: CSSProperties = {
    fontSize:   13,
    color:      "var(--color-text-tertiary)",
    transform:  open ? "rotate(180deg)" : "none",
    transition: "transform 0.2s",
  };

  const contentStyle: CSSProperties = {
    padding:    "10px 12px",
    fontSize:   12,
    color:      "var(--color-text-secondary)",
    lineHeight: 1.6,
    borderTop:  "0.5px solid var(--color-border-tertiary)",
    background: "var(--color-background-primary)",
  };

  return (
    <div style={wrapperStyle}>
      <button style={headerBtnStyle} onClick={() => setOpen((o) => !o)}>
        <span style={badgeStyle}>#{index + 1}</span>

        <span style={filenameStyle}>
          {filename} · chunk {source.chunk_index}
        </span>

        <div style={{ flex: "0 0 80px" }}>
          <SimilarityBar value={source.similarity} />
        </div>

        <span style={chevronStyle}>▾</span>
      </button>

      {open && <div style={contentStyle}>{source.content}</div>}
    </div>
  );
}