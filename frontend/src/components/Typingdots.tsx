import type { CSSProperties } from "react";

const DOT_INDICES = [0, 1, 2] as const;

export function TypingDots() {
  const containerStyle: CSSProperties = {
    display:      "flex",
    gap:          4,
    padding:      "10px 14px",
    background:   "var(--color-background-secondary)",
    border:       "0.5px solid var(--color-border-tertiary)",
    borderRadius: "16px 16px 16px 4px",
    width:        "fit-content",
    marginBottom: 20,
  };

  return (
    <div style={containerStyle}>
      {DOT_INDICES.map((i) => {
        const dotStyle: CSSProperties = {
          width:        6,
          height:       6,
          borderRadius: "50%",
          background:   "var(--color-text-tertiary)",
          display:      "inline-block",
          animation:    `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
        };
        return <span key={i} style={dotStyle} />;
      })}
      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40%           { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
}