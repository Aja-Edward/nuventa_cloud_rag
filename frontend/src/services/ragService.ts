import type { ApiStatus, AskResponse } from "../types/types";

const API_BASE = "http://localhost:8000";

export async function fetchHealth(): Promise<ApiStatus> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok ? "online" : "offline";
  } catch {
    return "offline";
  }
}

export async function fetchStats(): Promise<number | null> {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) return null;
    const data = await res.json();
    return typeof data.total_chunks === "number" ? data.total_chunks : null;
  } catch {
    return null;
  }
}

export async function askQuestion(
  question:            string,
  topK:                number = 5,
  similarityThreshold: number = 0.3
): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/ask`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({
      question,
      top_k:                topK,
      similarity_threshold: similarityThreshold,
    }),
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error((data as { detail?: string }).detail ?? "Request failed");
  }

  return data as AskResponse;
}