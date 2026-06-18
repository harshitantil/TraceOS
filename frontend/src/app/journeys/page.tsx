"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowDown } from "lucide-react";
import AppShell from "@/components/AppShell";
import { api, Journey } from "@/lib/api";

export default function JourneysPage() {
  const [journeys, setJourneys] = useState<Journey[]>([]);
  const [title, setTitle] = useState("");

  const load = () => api.journeys().then(setJourneys);
  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createJourney({ title });
    setTitle("");
    load();
  };

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-2">Trace Journeys</h1>
      <p className="text-[var(--text-muted)] text-sm mb-6">See the complete story from idea to outcome</p>

      <form onSubmit={create} className="flex gap-2 mb-8">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New journey title..."
          className="flex-1 border border-[var(--border-glass)] rounded-lg px-3 py-2 bg-transparent"
          required
        />
        <button type="submit" className="bg-trace-600 text-white px-4 py-2 rounded-lg text-sm">Create Journey</button>
      </form>

      <div className="space-y-8">
        {journeys.map((j, ji) => (
          <motion.div
            key={j.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: ji * 0.1 }}
            className="glass-card p-6"
          >
            <h2 className="text-xl font-bold mb-1">{j.title}</h2>
            {j.description && <p className="text-sm text-[var(--text-muted)] mb-6">{j.description}</p>}

            <div className="flex flex-col items-center gap-2">
              {j.steps.length === 0 && (
                <p className="text-sm text-[var(--text-muted)]">Add steps by linking entities to this journey</p>
              )}
              {j.steps.map((step, i) => (
                <div key={step.id} className="flex flex-col items-center w-full max-w-md">
                  <Link
                    href={`/entities/${step.entity_type}/${step.entity_id}`}
                    className="w-full glass-card p-4 text-center hover:shadow-md transition-shadow"
                  >
                    <span className="text-xs uppercase text-trace-600 font-medium">{step.entity_type}</span>
                    <p className="font-medium mt-1">{step.label}</p>
                  </Link>
                  {i < j.steps.length - 1 && <ArrowDown size={20} className="text-[var(--text-muted)] my-1" />}
                </div>
              ))}
            </div>
          </motion.div>
        ))}
        {journeys.length === 0 && <p className="text-[var(--text-muted)]">No journeys yet. Create one to trace your story.</p>}
      </div>
    </AppShell>
  );
}
