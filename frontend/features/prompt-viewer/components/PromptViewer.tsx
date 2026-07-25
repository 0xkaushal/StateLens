"use client";

import type { Event } from "@/types";

interface Message {
  role: string;
  content: string;
}

interface Props {
  event: Event | null;
}

function MessageBubble({ message }: { message: Message }) {
  const isSystem = message.role === "system";
  const isUser = message.role === "user";

  return (
    <div
      className={`rounded-lg p-3 text-sm ${
        isSystem
          ? "bg-neutral-800/60 border border-neutral-700/40"
          : isUser
          ? "bg-indigo-600/10 border border-indigo-500/20"
          : "bg-emerald-600/10 border border-emerald-500/20"
      }`}
    >
      <p
        className={`text-xs font-mono uppercase mb-2 ${
          isSystem
            ? "text-neutral-500"
            : isUser
            ? "text-indigo-400"
            : "text-emerald-400"
        }`}
      >
        {message.role}
      </p>
      <p className="text-neutral-200 whitespace-pre-wrap leading-relaxed">{message.content}</p>
    </div>
  );
}

export function PromptViewer({ event }: Props) {
  if (!event) {
    return (
      <div className="flex items-center justify-center h-32 text-sm text-neutral-500">
        Select a node to view its prompt.
      </div>
    );
  }

  if (event.nodeType !== "llm") {
    return (
      <div className="flex items-center justify-center h-32 text-sm text-neutral-500">
        Prompt viewer is only available for LLM nodes.
      </div>
    );
  }

  const messages = ((event.input?.messages ?? []) as unknown[]).map((m) => m as Message);
  const model = String(event.input?.model ?? "unknown");
  const temperature = event.input?.temperature as number | undefined;
  const usage = event.output?.usage as Record<string, number> | undefined;
  const responseContent = event.output?.content != null ? String(event.output.content) : null;

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Meta */}
      <div className="flex items-center gap-3 text-xs text-neutral-500">
        <span className="font-mono text-neutral-300">{model}</span>
        {temperature !== undefined && <span>temp: {temperature}</span>}
        {usage && (
          <span className="ml-auto">
            {usage.prompt_tokens}p / {usage.completion_tokens}c / {usage.total_tokens}t tokens
          </span>
        )}
      </div>

      {/* Messages */}
      <div className="flex flex-col gap-3">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
      </div>

      {/* Response */}
      {responseContent && (
        <div>
          <p className="text-xs text-neutral-500 uppercase tracking-wide mb-2">Response</p>
          <div className="rounded-lg bg-emerald-600/10 border border-emerald-500/20 p-3">
            <p className="text-xs font-mono uppercase text-emerald-400 mb-2">assistant</p>
            <p className="text-sm text-neutral-200 whitespace-pre-wrap leading-relaxed">
              {responseContent}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
