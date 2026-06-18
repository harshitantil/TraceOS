"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

export default function TimelinePage() {
  const [view, setView] = useState("weekly");
  const [events, setEvents] = useState<Array<{ id: string; title: string; entity_type: string; event_type: string; timestamp: string }>>([]);

  useEffect(() => {
    api.timeline(view).then(setEvents);
  }, [view]);

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">Activity Timeline</h1>
      <div className="flex gap-2 mb-6">
        {["daily", "weekly", "monthly"].map((v) => (
          <button
            key={v}
            onClick={() => setView(v)}
            className={`px-4 py-2 rounded-lg text-sm capitalize ${view === v ? "bg-trace-600 text-white" : "bg-white border border-slate-200"}`}
          >
            {v}
          </button>
        ))}
      </div>
      <div className="relative border-l-2 border-trace-200 ml-4 space-y-6">
        {events.map((e) => (
          <div key={e.id} className="relative pl-8">
            <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-trace-500 border-2 border-white" />
            <div className="bg-white border border-slate-200 rounded-xl p-4">
              <p className="font-medium text-slate-900">{e.title}</p>
              <p className="text-xs text-slate-500 mt-1">
                {e.entity_type} · {e.event_type} · {new Date(e.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
        {events.length === 0 && <p className="text-slate-500 pl-8">No events in this period.</p>}
      </div>
    </AppShell>
  );
}
