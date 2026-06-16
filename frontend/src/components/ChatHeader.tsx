import type { ReactNode } from "react";
import type { ApiStatus } from "../types/types";
import {
  GraduationCap,
  Wifi,
  WifiOff,
  LoaderCircle,
} from "lucide-react";

interface ChatHeaderProps {
  totalChunks: number | null;
  apiStatus: ApiStatus;
}

const STATUS: Record<
  ApiStatus,
  {
    icon: ReactNode;
    className: string;
    label: string;
  }
> = {
  online: {
    icon: <Wifi className="h-3.5 w-3.5" />,
    label: "Online",
    className:
      "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
  },
  offline: {
    icon: <WifiOff className="h-3.5 w-3.5" />,
    label: "Offline",
    className:
      "bg-red-50 text-red-700 ring-1 ring-red-200",
  },
  checking: {
    icon: <LoaderCircle className="h-3.5 w-3.5 animate-spin" />,
    label: "Checking",
    className:
      "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
  },
};

export function ChatHeader({
  totalChunks,
  apiStatus,
}: ChatHeaderProps) {
  const status = STATUS[apiStatus];

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 shadow-sm">
      <div className="flex items-center justify-center gap-4">
        {/* Logo */}
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-black text-white shadow-md">
          <GraduationCap className="h-6 w-6" />
        </div>

        {/* Heading */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">
            AI Assistant
          </p>

          <p className="text-sm text-slate-500">
            {totalChunks !== null
              ? `${totalChunks.toLocaleString()} knowledge chunks indexed`
              : "Loading knowledge base..."}
          </p>
        </div>
      </div>

      {/* Status */}
      <div
        className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium ${status.className}`}
      >
        {apiStatus === "online" && (
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
        )}

        {status.icon}
        {status.label}
      </div>
    </header>
  );
}