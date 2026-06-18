"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AppShell from "@/components/AppShell";
import { api, ActivityReplay } from "@/lib/api";

export default function ReplayPage() {
  const [start, setStart] = useState("2026-03-01");
  const [end, setEnd] = useState("2026-03-31");
  const [replay, setReplay] = useState<ActivityReplay | null>(null);
  const [playing, setPlaying] = useState(false);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.replay(start, end);
      setReplay(data);
      setIndex(0);
    } finally {
      setLoading(false);
    }
  };

  const play = () => {
    if (!replay?.events.length) return;
    setPlaying(true);
    setIndex(0);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setIndex(i);
      if (i >= replay.events.length - 1) {
        clearInterval(interval);
        setPlaying(false);
      }
    }, 800);
  };

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-2">Activity Replay</h1>
      <p className="text-[var(--text-muted)] text-sm mb-6">Replay company history like a timeline</p>

      <div className="flex flex-wrap gap-3 mb-8">
        <input type="date" value={start} onChange={(e) => setStart(e.target.value)} className="border border-[var(--border-glass)] rounded-lg px-3 py-2 bg-transparent text-sm" />
        <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} className="border border-[var(--border-glass)] rounded-lg px-3 py-2 bg-transparent text-sm" />
        <button onClick={load} disabled={loading} className="bg-trace-600 text-white px-4 py-2 rounded-lg text-sm">
          {loading ? "Loading..." : "Load Period"}
        </button>
        {replay && replay.events.length > 0 && (
          <button onClick={play} disabled={playing} className="glass-card px-4 py-2 rounded-lg text-sm">
            {playing ? "Playing..." : "▶ Replay"}
          </button>
        )}
      </div>

      {replay && (
        <div className="glass-card p-6">
          <p className="text-sm text-[var(--text-muted)] mb-4">{replay.total} events from {start} to {end}</p>
          <div className="relative border-l-2 border-trace-400 ml-4 space-y-1 min-h-[200px]">
            <AnimatePresence>
              {replay.events.slice(0, index + 1).map((e, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="relative pl-8 py-3"
                >
                  <div className="absolute -left-[9px] top-4 w-4 h-4 rounded-full bg-trace-500 ring-4 ring-trace-500/20" />
                  <p className="font-medium text-sm">{e.title}</p>
                  <p className="text-xs text-[var(--text-muted)]">
                    {e.entity_type} · {e.event_type} · {new Date(e.timestamp).toLocaleString()}
                  </p>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
    </AppShell>
  );
}
