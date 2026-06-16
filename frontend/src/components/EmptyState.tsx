import {
  GraduationCap,
} from "lucide-react";

const SUGGESTED_QUESTIONS = [
  "What is this system about?",
  "How does the authentication flow work?",
  "What features does the teacher portal have?",
  "How are exam results published?",
  "What is the tech stack used?",
];

interface EmptyStateProps {
  onSuggest: (question: string) => void;
}

export function EmptyState({ onSuggest }: EmptyStateProps) {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col items-center justify-center py-8">
      {/* Logo/Icon */}
      <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-2xl bg-black text-3xl text-white shadow-lg">
        <GraduationCap />
      </div>

      {/* Heading */}
      <h1 className="text-center text-4xl font-bold tracking-tight text-slate-900">
        School Knowledge Assistant
      </h1>

      <p className="mt-3 max-w-2xl text-center text-slate-600">
        Ask questions about the school management system. Every response is
        generated from your uploaded documentation and knowledge base.
      </p>

      {/* Suggested Questions */}
      <div className="mt-12 grid w-full gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SUGGESTED_QUESTIONS.map((question) => (
          <button
            key={question}
            onClick={() => onSuggest(question)}
            className="
              group
              rounded-2xl
              border
              border-slate-200
              bg-white
              p-5
              text-left
              shadow-sm
              transition-all
              duration-200
              hover:-translate-y-1
              hover:border-blue-500
              hover:shadow-lg
            "
          >
            <div className="mb-3 text-2xl">💬</div>

            <p className="font-medium text-slate-800 group-hover:text-blue-600">
              {question}
            </p>

            <p className="mt-2 text-sm text-slate-500">
              Click to ask this question
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}