"use client";

import { useState } from "react";
import type { Conversation, Event } from "@/types";
import { Features } from "@/config/features";
import { ConversationList } from "@/features/conversation";
import { Timeline, useEvents } from "@/features/timeline";
import { ExecutionGraph } from "@/features/execution-graph";
import { NodeInspector } from "@/features/node-inspector";
import { PromptViewer } from "@/features/prompt-viewer";
import { ToolViewer } from "@/features/tool-viewer";
import { StateViewer } from "@/features/state-viewer";
import { ExecutionSummary } from "@/features/execution-summary";

type InspectorTab = "node" | "prompt" | "tool" | "state";
type MainTab = "timeline" | "graph";

function Logo() {
  return (
    <div className="flex items-center gap-2 px-4 py-3 border-b border-neutral-800">
      <div className="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center">
        <span className="text-white text-xs font-bold">SL</span>
      </div>
      <span className="text-sm font-semibold text-white tracking-tight">StateLens</span>
      <span className="ml-auto text-xs text-neutral-600">v0.1</span>
    </div>
  );
}

function TabBar({
  tabs,
  active,
  onChange,
}: {
  tabs: { id: string; label: string }[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="flex items-center gap-0.5 px-3 py-2 border-b border-neutral-800">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
            active === tab.id
              ? "bg-indigo-600/20 text-indigo-300"
              : "text-neutral-500 hover:text-neutral-300"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export default function DebuggerPage() {
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [mainTab, setMainTab] = useState<MainTab>("timeline");
  const [inspectorTab, setInspectorTab] = useState<InspectorTab>("node");

  const { events, loading: eventsLoading } = useEvents(
    selectedConversation?.id ?? null
  );

  function handleSelectConversation(conv: Conversation) {
    setSelectedConversation(conv);
    setSelectedEvent(null);
  }

  function handleSelectEvent(event: Event) {
    setSelectedEvent(event);
    // Auto-switch inspector tab based on node type
    if (event.nodeType === "llm") setInspectorTab("prompt");
    else if (event.nodeType === "tool") setInspectorTab("tool");
    else setInspectorTab("node");
  }

  const mainTabs = [
    ...(Features.timeline ? [{ id: "timeline", label: "Timeline" }] : []),
    ...(Features.graphView ? [{ id: "graph", label: "Execution Graph" }] : []),
  ];

  const inspectorTabs = [
    { id: "node", label: "Inspector" },
    ...(Features.promptViewer ? [{ id: "prompt", label: "Prompt" }] : []),
    ...(Features.toolViewer ? [{ id: "tool", label: "Tool" }] : []),
    ...(Features.stateViewer ? [{ id: "state", label: "State" }] : []),
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-neutral-950">
      {/* Sidebar: Conversations */}
      <aside className="w-64 shrink-0 flex flex-col border-r border-neutral-800 bg-neutral-950">
        <Logo />
        <div className="px-4 py-2">
          <p className="text-xs text-neutral-500 uppercase tracking-wide">Conversations</p>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ConversationList
            selectedId={selectedConversation?.id}
            onSelect={handleSelectConversation}
          />
        </div>
      </aside>

      {/* Main area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top: Timeline or Graph */}
        <div className="flex flex-col border-b border-neutral-800" style={{ height: "55%" }}>
          {mainTabs.length > 0 && (
            <TabBar
              tabs={mainTabs}
              active={mainTab}
              onChange={(id) => setMainTab(id as MainTab)}
            />
          )}

          {!selectedConversation ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <p className="text-4xl mb-3">◈</p>
                <p className="text-sm text-neutral-500">Select a conversation to begin debugging</p>
              </div>
            </div>
          ) : eventsLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <p className="text-sm text-neutral-500">Loading events...</p>
            </div>
          ) : (
            <div className="flex-1 overflow-auto">
              {mainTab === "timeline" && Features.timeline && (
                <Timeline
                  events={events}
                  selectedNodeId={selectedEvent?.nodeId}
                  onSelect={handleSelectEvent}
                />
              )}
              {mainTab === "graph" && Features.graphView && (
                <ExecutionGraph
                  events={events}
                  selectedNodeId={selectedEvent?.nodeId}
                  onSelectNode={handleSelectEvent}
                />
              )}
            </div>
          )}
        </div>

        {/* Bottom: Inspector panels */}
        <div className="flex-1 flex min-h-0">
          {/* Left: Inspector / Prompt / Tool / State */}
          <div className="flex-1 flex flex-col border-r border-neutral-800 overflow-hidden">
            <TabBar
              tabs={inspectorTabs}
              active={inspectorTab}
              onChange={(id) => setInspectorTab(id as InspectorTab)}
            />
            <div className="flex-1 overflow-y-auto">
              {inspectorTab === "node" && Features.nodeInspector && (
                <NodeInspector event={selectedEvent} />
              )}
              {inspectorTab === "prompt" && Features.promptViewer && (
                <PromptViewer event={selectedEvent} />
              )}
              {inspectorTab === "tool" && Features.toolViewer && (
                <ToolViewer event={selectedEvent} />
              )}
              {inspectorTab === "state" && Features.stateViewer && (
                <StateViewer event={selectedEvent} />
              )}
            </div>
          </div>

          {/* Right: Execution Summary */}
          {Features.executionSummary && selectedConversation && (
            <div className="w-64 shrink-0 overflow-y-auto">
              <div className="px-4 pt-3 pb-1">
                <p className="text-xs text-neutral-500 uppercase tracking-wide">Summary</p>
              </div>
              <ExecutionSummary
                conversation={selectedConversation}
                events={events}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
