"use client";

import type { Event } from "@/types";

interface Props {
  event: Event | null;
}

function JsonBlock({ value }: { value: unknown }) {
  return (
    <pre className="text-xs text-neutral-300 bg-neutral-800/60 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap border border-neutral-700/40">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

export function ToolViewer({ event }: Props) {
  if (!event) {
    return (
      <div className="flex items-center justify-center h-32 text-sm text-neutral-500">
        Select a node to view tool calls.
      </div>
    );
  }

  if (event.nodeType !== "tool") {
    return (
      <div className="flex items-center justify-center h-32 text-sm text-neutral-500">
        Tool viewer is only available for tool nodes.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <div>
        <p className="text-xs text-neutral-500 uppercase tracking-wide mb-2">Tool Name</p>
        <p className="text-sm font-semibold text-blue-400">{event.nodeName}</p>
      </div>

      <div>
        <p className="text-xs text-neutral-500 uppercase tracking-wide mb-2">Input</p>
        <JsonBlock value={event.input} />
      </div>

      <div>
        <p className="text-xs text-neutral-500 uppercase tracking-wide mb-2">Output</p>
        <JsonBlock value={event.output} />
      </div>

      {event.error && (
        <div>
          <p className="text-xs text-red-400 uppercase tracking-wide mb-2">Error</p>
          <pre className="text-xs text-red-300 bg-red-500/10 rounded-lg p-3 border border-red-500/20 whitespace-pre-wrap">
            {event.error}
          </pre>
        </div>
      )}
    </div>
  );
}
