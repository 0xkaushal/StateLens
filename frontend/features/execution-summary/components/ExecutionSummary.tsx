"use client";

import type { Event, Conversation } from "@/types";
import { formatDuration } from "@/shared/utils/time";

interface Props {
  conversation: Conversation;
  events: Event[];
}

export function ExecutionSummary({ conversation, events }: Props) {
  const failedEvents = events.filter((e) => e.status === "failed");
  const successEvents = events.filter((e) => e.status === "success");
  const nodeTypeCounts = events.reduce<Record<string, number>>((acc, e) => {
    acc[e.nodeType] = (acc[e.nodeType] ?? 0) + 1;
    return acc;
  }, {});

  const totalLatency = events.reduce((sum, e) => sum + e.latencyMs, 0);
  const slowestNode = events.reduce<Event | null>(
    (max, e) => (!max || e.latencyMs > max.latencyMs ? e : max),
    null
  );

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Title */}
      <div>
        <h3 className="text-base font-semibold text-white truncate">{conversation.title}</h3>
        <p className="text-xs text-neutral-500 font-mono mt-0.5">{conversation.id}</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: "Total Nodes", value: events.length },
          { label: "Total Latency", value: formatDuration(totalLatency) },
          {
            label: "Success",
            value: successEvents.length,
            color: "text-emerald-400",
          },
          {
            label: "Failed",
            value: failedEvents.length,
            color: failedEvents.length > 0 ? "text-red-400" : "text-neutral-400",
          },
        ].map((stat) => (
          <div key={stat.label} className="rounded-lg bg-neutral-800/40 p-3">
            <p className="text-xs text-neutral-500">{stat.label}</p>
            <p className={`text-lg font-semibold ${stat.color ?? "text-white"}`}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Node type breakdown */}
      <div>
        <p className="text-xs text-neutral-500 uppercase tracking-wide mb-2">Node Types</p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(nodeTypeCounts).map(([type, count]) => (
            <span
              key={type}
              className="rounded-full bg-indigo-600/10 border border-indigo-500/20 px-2.5 py-0.5 text-xs text-indigo-300"
            >
              {type}: {count}
            </span>
          ))}
        </div>
      </div>

      {/* Slowest node */}
      {slowestNode && (
        <div>
          <p className="text-xs text-neutral-500 uppercase tracking-wide mb-2">Slowest Node</p>
          <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-3">
            <p className="text-sm text-amber-300 font-medium">{slowestNode.nodeName}</p>
            <p className="text-xs text-neutral-400 mt-0.5">
              {formatDuration(slowestNode.latencyMs)} — {slowestNode.nodeType}
            </p>
          </div>
        </div>
      )}

      {/* Errors */}
      {failedEvents.length > 0 && (
        <div>
          <p className="text-xs text-red-400 uppercase tracking-wide mb-2">Errors</p>
          <div className="flex flex-col gap-2">
            {failedEvents.map((e) => (
              <div
                key={e.nodeId}
                className="rounded-lg bg-red-500/10 border border-red-500/20 p-3"
              >
                <p className="text-xs font-semibold text-red-300">{e.nodeName}</p>
                {e.error && (
                  <p className="text-xs text-neutral-400 mt-1 font-mono line-clamp-2">{e.error}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
