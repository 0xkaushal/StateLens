"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { Event, NodeType } from "@/types";
import { formatDuration } from "@/shared/utils/time";

const NODE_COLORS: Record<NodeType, string> = {
  llm: "#7c3aed",
  tool: "#2563eb",
  memory: "#d97706",
  planner: "#4f46e5",
  router: "#0d9488",
};

function eventsToGraph(events: Event[], selectedNodeId?: string) {
  const nodes: Node[] = events.map((event, i) => ({
    id: event.nodeId,
    position: { x: i * 200, y: 100 },
    data: {
      label: event.nodeName,
      nodeType: event.nodeType,
      status: event.status,
      latencyMs: event.latencyMs,
      error: event.error,
    },
    type: "stateNode",
    selected: event.nodeId === selectedNodeId,
  }));

  const edges: Edge[] = events.slice(1).map((event, i) => ({
    id: `edge-${i}`,
    source: events[i].nodeId,
    target: event.nodeId,
    animated: true,
    style: { stroke: events[i].status === "failed" ? "#ef4444" : "#4f46e5", strokeWidth: 2 },
  }));

  return { nodes, edges };
}

interface StateNodeData extends Record<string, unknown> {
  label: string;
  nodeType: NodeType;
  status: "success" | "failed";
  latencyMs: number;
  error?: string;
}

function StateNode({ data, selected }: { data: StateNodeData; selected: boolean }) {
  const color = NODE_COLORS[data.nodeType];
  return (
    <div
      className={`rounded-xl border-2 px-4 py-3 min-w-[140px] bg-neutral-900 shadow-lg transition-all ${
        selected ? "ring-2 ring-indigo-400 ring-offset-1 ring-offset-neutral-950" : ""
      }`}
      style={{ borderColor: data.status === "failed" ? "#ef4444" : color }}
    >
      <div
        className="text-xs font-mono mb-1 uppercase tracking-wide"
        style={{ color }}
      >
        {data.nodeType}
      </div>
      <div className="text-sm font-semibold text-white">{data.label}</div>
      <div className="text-xs text-neutral-400 mt-1">{formatDuration(data.latencyMs)}</div>
      {data.status === "failed" && (
        <div className="text-xs text-red-400 mt-1">failed</div>
      )}
    </div>
  );
}

const nodeTypes = { stateNode: StateNode };

interface Props {
  events: Event[];
  selectedNodeId?: string;
  onSelectNode: (event: Event) => void;
}

export function ExecutionGraph({ events, selectedNodeId, onSelectNode }: Props) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => eventsToGraph(events, selectedNodeId),
    [events, selectedNodeId]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const event = events.find((e) => e.nodeId === node.id);
      if (event) onSelectNode(event);
    },
    [events, onSelectNode]
  );

  if (events.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-neutral-500">
        No execution graph available.
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        className="bg-neutral-950"
      >
        <Background color="#333" gap={16} />
        <Controls className="!bg-neutral-800 !border-neutral-700" />
        <MiniMap
          nodeColor={(n) => {
            const d = n.data as StateNodeData;
            return d.status === "failed" ? "#ef4444" : NODE_COLORS[d.nodeType];
          }}
          className="!bg-neutral-900 !border-neutral-700"
        />
      </ReactFlow>
    </div>
  );
}
