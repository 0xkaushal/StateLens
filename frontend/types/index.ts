/**
 * Canonical Event model — mirrors contracts/event.schema.json
 */

export type NodeType = "llm" | "tool" | "memory" | "planner" | "router";
export type EventStatus = "success" | "failed";

export interface Event {
  conversationId: string;
  nodeId: string;
  nodeName: string;
  nodeType: NodeType;
  startTime: string;
  endTime: string;
  latencyMs: number;
  status: EventStatus;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  stateBefore: Record<string, unknown>;
  stateAfter: Record<string, unknown>;
  error?: string;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  status: EventStatus;
  totalEvents: number;
  totalLatencyMs: number;
}
