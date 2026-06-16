import type { KeyboardEvent, RefObject } from "react";
import { ArrowUp, LoaderCircle } from "lucide-react";

interface ChatInputProps {
  input: string;
  setInput: (val: string) => void;
  loading: boolean;
  onSend: () => void;
  onKeyDown: (e: KeyboardEvent<HTMLTextAreaElement>) => void;
  inputRef: RefObject<HTMLTextAreaElement | null>;
}

export function ChatInput({
  input,
  setInput,
  loading,
  onSend,
  onKeyDown,
  inputRef,
}: ChatInputProps) {
  const disabled = loading || !input.trim();

  return (
    <div className="border-t border-slate-200 bg-white px-6 py-5">
      <div className="mx-auto max-w-4xl">
        <div className="flex items-end gap-3 rounded-3xl border border-slate-300 bg-white px-4 py-3 shadow-sm transition-all focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
            placeholder="Ask about authentication, exams, users, setup..."
            className="max-h-32 flex-1 resize-none overflow-y-auto bg-transparent text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none"
            onInput={(e) => {
              const target = e.currentTarget;
              target.style.height = "auto";
              target.style.height =
                Math.min(target.scrollHeight, 128) + "px";
            }}
          />

          <button
            onClick={onSend}
            disabled={disabled}
            className={`
              flex h-10 w-10 items-center justify-center rounded-full
              transition-all duration-200
              ${
                disabled
                  ? "cursor-not-allowed bg-slate-200 text-slate-400"
                  : "bg-blue-600 text-white hover:bg-blue-700 active:scale-95"
              }
            `}
          >
            {loading ? (
              <LoaderCircle className="h-5 w-5 animate-spin" />
            ) : (
              <ArrowUp className="h-5 w-5" />
            )}
          </button>
        </div>

        <p className="mt-3 text-center text-xs text-slate-500">
          Press <span className="font-medium">Enter</span> to send ·{" "}
          <span className="font-medium">Shift + Enter</span> for a new line
        </p>
      </div>
    </div>
  );
}