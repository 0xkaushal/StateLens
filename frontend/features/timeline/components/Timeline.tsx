"use client";

import type { Event, NodeType } from "@/types";
import { formatDuration, formatTime } from "@/shared/utils/time";

const NODE_COLORS: Record<NodeType, string> = {
  llm: "bg-violet-500",
  tool: "bg-blue-500",
  memory: "bg-amber-500",
  planner: "bg-indigo-500",
  router: "bg-teal-500",
};

const NODE_LABEL_COLORS: Record<NodeType, string> = {
  llm: "text-violet-400",
  tool: "text-blue-400",
  memory: "text-amber-400",
  planner: "text-indigo-400",
  router: "text-teal-400",
};

interface Props {
  events: Event[];
  selectedNodeId?: string;
  onSelect: (event: Event) => void;
}

export function Timeline({ events, selectedNodeId, onSelect }: Props) {
  if (events.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-sm text-neutral-500">
        No events to display.
      </div>
    );
  }

  const tStart = new Date(events[0].startTime).getTime();
  const tEnd = Math.max(...events.map((e) => new Date(e.endTime).getTime()));
  const totalMs = tEnd - tStart || 1;

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[600px]">
        {/* Header */}
        <div className="flex items-center gap-3 px-4 py-2 border-b border-neutral-800 text-xs text-neutral-500">
          <span className="w-32 shrink-0">Node</span>
          <span className="w-16 shrink-0">Type</span>
          <span className="flex-1">Timeline</span>
          <span className="w-16 text-right shrink-0">Latency</span>
          <span className="w-16 text-right shrink-0">Status</span>
        </div>

        {/* Rows */}
        {events.map((event) => {
          const eStart = new Date(event.startTime).getTime();
          const offsetPct = ((eStart - tStart) / totalMs) * 100;
          const widthPct = Math.max((event.latencyMs / totalMs) * 100, 1);
          const isSelected = selectedNodeId === event.nodeId;
          const barColor = NODE_COLORS[event.nodeType];

          return (
            <button
              key={event.nodeId}
              onClick={() => onSelect(event)}
              className={`w-full flex items-center gap-3 px-4 py-2 text-left transition-colors ${
                isSelected
                  ? "bg-indigo-600/10 border-l-2 border-indigo-500"
                  : "hover:bg-neutral-800/40 border-l-2 border-transparent"
              }`}
            >
              <span className="w-32 shrink-0 text-sm font-medium text-neutral-200 truncate">
                {event.nodeName}
              </span>
              <span
                className={`w-16 shrink-0 text-xs font-mono ${NODE_LABEL_COLORS[event.nodeType]}`}
              >
                {event.nodeType}
              </span>
              <div className="flex-1 relative h-5">
                <div
                  className={`absolute top-0.5 h-4 rounded ${barColor} ${
                    event.status === "failed" ? "opacity-50 border border-red-400" : "opacity-80"
                  }`}
                  style={{ left: `${offsetPct}%`, width: `${widthPct}%` }}
                  title={`${formatTime(event.startTime)} → ${formatTime(event.endTime)}`}
                />
              </div>
              <span className="w-16 text-right shrink-0 text-xs font-mono text-neutral-400">
                {formatDuration(event.latencyMs)}
              </span>
              <span className="w-16 text-right shrink-0">
                {event.status === "success" ? (
                  <span className="text-xs text-emerald-400">ok</span>
                ) : (
                  <span className="text-xs text-red-400">err</span>
                )}
              </span>
            </button>
          );
        })}

        {/* Total bar */}
        <div className="px-4 py-2 border-t border-neutral-800 flex items-center justify-between text-xs text-neutral-500">
          <span>Total: {events.length} nodes</span>
          <span>{formatDuration(totalMs)}</span>
        </div>
      </div>
    </div>
  );
}
