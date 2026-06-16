import { useState, useRef, useEffect, useCallback } from "react";
import type { RefObject, KeyboardEvent } from "react";
import { askQuestion } from "../services/ragService"
import type { ChatMessage } from "../types/types";

interface UseChatReturn {
  messages:     ChatMessage[];
  input:        string;
  setInput:     (val: string) => void;
  loading:      boolean;
  sendQuestion: (override?: string) => Promise<void>;
  handleKey:    (e: KeyboardEvent<HTMLTextAreaElement>) => void;
  bottomRef:    RefObject<HTMLDivElement | null>;   // ← add | null
  inputRef:     RefObject<HTMLTextAreaElement | null>; // ← add | null
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input,    setInput]    = useState<string>("");
  const [loading,  setLoading]  = useState<boolean>(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendQuestion = useCallback(
    async (override?: string): Promise<void> => {
      const question = (override ?? input).trim();
      if (!question || loading) return;

      setInput("");
      setMessages((prev) => [...prev, { role: "user", content: question }]);
      setLoading(true);

      try {
        const result = await askQuestion(question);
        setMessages((prev) => [
          ...prev,
          {
            role:       "assistant",
            content:    result.answer,
            sources:    result.sources,
            elapsed_ms: result.elapsed_ms,
          },
        ]);
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          {
            role:    "assistant",
            content: "Something went wrong. Make sure the FastAPI server is running on port 8000.",
            error:   err instanceof Error ? err.message : "Unknown error",
          },
        ]);
      } finally {
        setLoading(false);
        setTimeout(() => inputRef.current?.focus(), 50);
      }
    },
    [input, loading]
  );

  const handleKey = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>): void => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQuestion();
      }
    },
    [sendQuestion]
  );

  return {
    messages,
    input,
    setInput,
    loading,
    sendQuestion,
    handleKey,
    bottomRef,
    inputRef,
  };
}