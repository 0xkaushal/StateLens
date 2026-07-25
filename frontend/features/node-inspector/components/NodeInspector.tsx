"use client";

import type { Event } from "@/types";
import { formatDuration, formatTime } from "@/shared/utils/time";

const NODE_TYPE_ICONS: Record<string, string> = {
  llm: "◈",
  tool: "⚙",
  memory: "◎",
  planner: "◇",
  router: "⟆",
};

interface Props {
  event: Event | null;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs text-neutral-500 uppercase tracking-wide mb-1">{label}</p>
      <div className="text-sm text-neutral-200">{children}</div>
    </div>
  );
}

export function NodeInspector({ event }: Props) {
  if (!event) {
    return (
      <div className="flex items-center justify-center h-32 text-sm text-neutral-500">
        Select a node to inspect.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-5 p-4">
      {/* Header */}
      <div className="flex items-start gap-3">
        <span className="text-2xl text-neutral-400">{NODE_TYPE_ICONS[event.nodeType]}</span>
        <div>
          <h3 className="text-base font-semibold text-white">{event.nodeName}</h3>
          <p className="text-xs text-neutral-500 font-mono">{event.nodeId}</p>
        </div>
        <div className="ml-auto">
          {event.status === "success" ? (
            <span className="rounded-full bg-emerald-500/10 text-emerald-400 px-2 py-0.5 text-xs">success</span>
          ) : (
            <span className="rounded-full bg-red-500/10 text-red-400 px-2 py-0.5 text-xs">failed</span>
          )}
        </div>
      </div>

      {/* Timing */}
      <div className="grid grid-cols-2 gap-3 rounded-lg bg-neutral-800/40 p-3">
        <Field label="Start">{formatTime(event.startTime)}</Field>
        <Field label="End">{formatTime(event.endTime)}</Field>
        <Field label="Latency">{formatDuration(event.latencyMs)}</Field>
        <Field label="Type">
          <span className="font-mono text-indigo-400">{event.nodeType}</span>
        </Field>
      </div>

      {/* Error */}
      {event.error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
          <p className="text-xs text-red-400 font-mono uppercase mb-1">Error</p>
          <p className="text-sm text-red-300 font-mono whitespace-pre-wrap">{event.error}</p>
        </div>
      )}
    </div>
  );
}
