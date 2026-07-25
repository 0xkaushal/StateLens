"use client";

import type { Event } from "@/types";

interface Props {
  event: Event | null;
}

type DiffEntry = {
  key: string;
  before: unknown;
  after: unknown;
  changed: boolean;
};

function computeDiff(before: Record<string, unknown>, after: Record<string, unknown>): DiffEntry[] {
  const keys = Array.from(new Set([...Object.keys(before), ...Object.keys(after)]));
  return keys.map((key) => ({
    key,
    before: before[key],
    after: after[key],
    changed: JSON.stringify(before[key]) !== JSON.stringify(after[key]),
  }));
}

function ValueCell({ value, highlight }: { value: unknown; highlight?: "add" | "remove" }) {
  const base = "text-xs font-mono px-2 py-1 rounded";
  const color =
    highlight === "add"
      ? "bg-emerald-500/10 text-emerald-300"
      : highlight === "remove"
      ? "bg-red-500/10 text-red-300"
      : "text-neutral-400";
  return (
    <span className={`${base} ${color}`}>
      {value === undefined ? <span className="italic text-neutral-600">—</span> : JSON.stringify(value)}
    </span>
  );
}

export function StateViewer({ event }: Props) {
  if (!event) {
    return (
      <div className="flex items-center justify-center h-32 text-sm text-neutral-500">
        Select a node to view state transitions.
      </div>
    );
  }

  const diff = computeDiff(event.stateBefore, event.stateAfter);

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="grid grid-cols-3 gap-2 text-xs text-neutral-500 uppercase tracking-wide border-b border-neutral-800 pb-2">
        <span>Key</span>
        <span>Before</span>
        <span>After</span>
      </div>
      {diff.map((entry) => (
        <div key={entry.key} className={`grid grid-cols-3 gap-2 items-start rounded-lg px-2 py-1.5 ${entry.changed ? "bg-neutral-800/30" : ""}`}>
          <span className={`text-xs font-mono ${entry.changed ? "text-white" : "text-neutral-500"}`}>
            {entry.key}
          </span>
          <ValueCell
            value={entry.before}
            highlight={entry.changed && entry.before !== undefined ? "remove" : undefined}
          />
          <ValueCell
            value={entry.after}
            highlight={entry.changed && entry.after !== undefined ? "add" : undefined}
          />
        </div>
      ))}
      {diff.length === 0 && (
        <p className="text-sm text-neutral-500 text-center py-4">No state keys found.</p>
      )}
      <div className="text-xs text-neutral-600 mt-2">
        {diff.filter((d) => d.changed).length} changed / {diff.length} total keys
      </div>
    </div>
  );
}
