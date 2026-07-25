/**
 * Feature Registry
 * All feature flags are defined here. Never access environment variables
 * directly outside this file.
 */

function flag(key: string, fallback = false): boolean {
  const val = process.env[key];
  if (val === undefined) return fallback;
  return val === "true";
}

export const Features = {
  timeline: flag("NEXT_PUBLIC_FEATURE_TIMELINE", true),
  graphView: flag("NEXT_PUBLIC_FEATURE_GRAPH_VIEW", true),
  nodeInspector: flag("NEXT_PUBLIC_FEATURE_NODE_INSPECTOR", true),
  promptViewer: flag("NEXT_PUBLIC_FEATURE_PROMPT_VIEWER", true),
  toolViewer: flag("NEXT_PUBLIC_FEATURE_TOOL_VIEWER", true),
  stateViewer: flag("NEXT_PUBLIC_FEATURE_STATE_VIEWER", true),
  executionSummary: flag("NEXT_PUBLIC_FEATURE_EXECUTION_SUMMARY", true),
  replay: flag("NEXT_PUBLIC_FEATURE_REPLAY", false),
  search: flag("NEXT_PUBLIC_FEATURE_SEARCH", false),
  aiSummary: flag("NEXT_PUBLIC_FEATURE_AI_SUMMARY", false),
  darkMode: flag("NEXT_PUBLIC_FEATURE_DARK_MODE", true),
} as const;

export type FeatureKey = keyof typeof Features;
