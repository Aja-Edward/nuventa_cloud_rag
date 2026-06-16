// ── API / domain types ────────────────────────────────────────────────────────

export type ApiStatus = "checking" | "online" | "offline";

export interface SourceChunk {
  content:     string;
  source:      string;
  chunk_index: number;
  similarity:  number;
}

export interface AskResponse {
  answer:     string;
  sources:    SourceChunk[];
  elapsed_ms: number;
}

// ── Chat message types ────────────────────────────────────────────────────────

interface BaseMessage {
  role:    "user" | "assistant";
  content: string;
}

export interface UserMessage extends BaseMessage {
  role: "user";
}

export interface AssistantMessage extends BaseMessage {
  role:        "assistant";
  sources?:    SourceChunk[];
  elapsed_ms?: number;
  error?:      string;
}

export type ChatMessage = UserMessage | AssistantMessage;