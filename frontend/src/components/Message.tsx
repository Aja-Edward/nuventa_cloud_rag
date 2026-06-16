import {
  GraduationCap,
  Clock3,
  User,
  TriangleAlert,
} from "lucide-react";
import { SourceCard } from "./Sourcecard";
import type {
  AssistantMessage,
  ChatMessage,
} from "../types/types";

interface MessageProps {
  msg: ChatMessage;
}

export function Message({ msg }: MessageProps) {
  const isUser = msg.role === "user";

  if (isUser) {
    return (
      <div className="mb-8 flex justify-end">
        <div className="max-w-2xl rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-md">
          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wide text-slate-300">
            <User className="h-3.5 w-3.5" />
            You
          </div>

          <p className="whitespace-pre-wrap leading-7">
            {msg.content}
          </p>
        </div>
      </div>
    );
  }

  const assistant = msg as AssistantMessage;

  return (
    <article className="mb-10 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
      {/* Header */}

      <header className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-black text-white">
            <GraduationCap className="h-6 w-6" />
          </div>

          <div>
            <h3 className="font-semibold text-slate-900">
              School Knowledge Assistant
            </h3>

            <p className="text-sm text-slate-500">
              Verified answer from indexed documentation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-600">
          <Clock3 className="h-4 w-4" />
          {assistant.elapsed_ms} ms
        </div>
      </header>

      {/* Answer */}

      <section className="prose prose-slate max-w-none px-8 py-7">
        {assistant.content}
      </section>

      {/* Sources */}

      {!!assistant.sources?.length && (
        <footer className="border-t border-slate-100 bg-slate-50 px-6 py-5">
          <h4 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Supporting Sources
          </h4>

          <div className="space-y-3">
            {assistant.sources.map((source, index) => (
              <SourceCard
                key={index}
                source={source}
                index={index}
              />
            ))}
          </div>
        </footer>
      )}

      {assistant.error && (
        <div className="flex items-center gap-2 border-t border-red-100 bg-red-50 px-6 py-4 text-red-700">
          <TriangleAlert className="h-5 w-5" />

          {assistant.error}
        </div>
      )}
    </article>
  );
}