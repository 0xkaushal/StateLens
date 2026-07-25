"use client";

import { useConversations } from "../hooks/useConversations";
import type { Conversation } from "@/types";
import { formatDistanceToNow } from "@/shared/utils/time";

interface Props {
  selectedId?: string;
  onSelect: (conv: Conversation) => void;
}

function StatusBadge({ status }: { status: Conversation["status"] }) {
  const base = "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium";
  if (status === "success") {
    return (
      <span className={`${base} bg-emerald-500/10 text-emerald-400`}>
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 inline-block" />
        success
      </span>
    );
  }
  return (
    <span className={`${base} bg-red-500/10 text-red-400`}>
      <span className="h-1.5 w-1.5 rounded-full bg-red-400 inline-block" />
      failed
    </span>
  );
}

export function ConversationList({ selectedId, onSelect }: Props) {
  const { conversations, loading, error } = useConversations();

  if (loading) {
    return (
      <div className="flex flex-col gap-2 p-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 rounded-lg bg-neutral-800/50 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-sm text-red-400">Failed to load conversations.</div>
    );
  }

  return (
    <ul className="flex flex-col gap-1 p-2">
      {conversations.map((conv) => (
        <li key={conv.id}>
          <button
            onClick={() => onSelect(conv)}
            className={`w-full text-left rounded-lg px-3 py-3 transition-colors ${
              selectedId === conv.id
                ? "bg-indigo-600/20 border border-indigo-500/30"
                : "hover:bg-neutral-800/60 border border-transparent"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm font-medium text-neutral-100 truncate leading-snug">
                {conv.title}
              </p>
              <StatusBadge status={conv.status} />
            </div>
            <div className="mt-1 flex items-center gap-3 text-xs text-neutral-500">
              <span>{conv.totalEvents} events</span>
              <span>{conv.totalLatencyMs}ms</span>
              <span className="ml-auto">{formatDistanceToNow(conv.updatedAt)}</span>
            </div>
          </button>
        </li>
      ))}
    </ul>
  );
}
