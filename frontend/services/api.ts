import type { Conversation, Event } from "@/types";
import mockData from "@/mock/conversation.json";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export async function getConversations(): Promise<Conversation[]> {
  if (USE_MOCK) {
    return mockData.conversations as Conversation[];
  }
  return fetchJSON<Conversation[]>("/conversations");
}

export async function getConversation(id: string): Promise<Conversation> {
  if (USE_MOCK) {
    const conv = mockData.conversations.find((c) => c.id === id);
    if (!conv) throw new Error(`Conversation ${id} not found`);
    return conv as Conversation;
  }
  return fetchJSON<Conversation>(`/conversations/${id}`);
}

export async function getEvents(conversationId: string): Promise<Event[]> {
  if (USE_MOCK) {
    const events = (mockData.events as Record<string, unknown[]>)[conversationId];
    if (!events) return [];
    return events as Event[];
  }
  return fetchJSON<Event[]>(`/events/${conversationId}`);
}

export async function checkHealth(): Promise<{ status: string }> {
  if (USE_MOCK) return { status: "ok" };
  return fetchJSON<{ status: string }>("/health");
}
