"use client";

import { useEffect, useState } from "react";
import { getEvents } from "@/services/api";
import type { Event } from "@/types";

export function useEvents(conversationId: string | null) {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!conversationId) return;
    setLoading(true);
    setError(null);
    getEvents(conversationId)
      .then(setEvents)
      .catch((e: unknown) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [conversationId]);

  return { events, loading, error };
}
