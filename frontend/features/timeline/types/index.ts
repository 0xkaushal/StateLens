import type { Event } from "@/types";

export type { Event };

export interface TimelineRow {
  event: Event;
  offsetMs: number;
  totalMs: number;
}
