"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import AppShell from "@/components/AppShell";
import IntelligentOrb from "@/components/IntelligentOrb";
import { api, FounderDashboard, PersonalDashboard, ProjectHealth } from "@/lib/api";

export default function DashboardPage() {
  const [tab, setTab] = useState<"founder" | "personal">("founder");
  const [founder, setFounder] = useState<FounderDashboard | null>(null);
  const [personal, setPersonal] = useState<PersonalDashboard | null>(null);
  const [health, setHealth] = useState<ProjectHealth[]>([]);
  const [digest, setDigest] = useState("");

  useEffect(() => {
    api.founderDashboard().then(setFounder);
    api.personalDashboard().then(setPersonal);
    api.projectHealth().then(setHealth);
    api.digest().then((d) => setDigest(d.ai_summary));
  }, []);

  const statusColor = { green: "bg-green-500", yellow: "bg-yellow-500", red: "bg-red-500" };

  return (
    <AppShell>
      <div className="flex gap-2 mb-8">
        {(["founder", "personal"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-xl text-sm capitalize transition-colors ${
              tab === t ? "bg-trace-600 text-white" : "glass-card text-[var(--text-muted)]"
            }`}
          >
            {t} Dashboard
          </button>
        ))}
      </div>

      {tab === "founder" && founder && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          <div className="glass-card p-6">
            <IntelligentOrb />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Active Projects", value: founder.stats.projects },
              { label: "Total Tasks", value: founder.stats.tasks },
              { label: "Overdue", value: founder.stats.overdue_tasks },
              { label: "Revenue", value: `$${founder.revenue_total.toLocaleString()}` },
            ].map((c) => (
              <div key={c.label} className="glass-card p-5">
                <p className="text-2xl font-bold">{c.value}</p>
                <p className="text-xs text-[var(--text-muted)] mt-1">{c.label}</p>
              </div>
            ))}
          </div>

          {founder.monthly_revenue.length > 0 && (
            <div className="glass-card p-6">
              <h2 className="font-semibold mb-4">Revenue</h2>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={founder.monthly_revenue}>
                    <XAxis dataKey="month" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(0, 7)} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="total" fill="#4f6ef7" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h2 className="font-semibold mb-3 text-red-600">Risks</h2>
              {founder.risks.map((r) => (
                <p key={r.id} className="text-sm py-1.5 border-b border-[var(--border-glass)]">{r.title}</p>
              ))}
              {founder.risks.length === 0 && <p className="text-sm text-[var(--text-muted)]">No risks detected</p>}
            </div>
            <div className="glass-card p-6">
              <h2 className="font-semibold mb-3">AI Summary</h2>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed">{digest || founder.ai_summary}</p>
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="font-semibold mb-4">Project Health</h2>
            <div className="space-y-3">
              {health.map((p) => (
                <div key={p.id} className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${statusColor[p.status]}`} />
                  <span className="text-sm flex-1">{p.name}</span>
                  <span className="text-xs text-[var(--text-muted)]">{p.progress}% · {p.overdue} overdue</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {tab === "personal" && personal && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h2 className="font-semibold mb-3">Daily Tasks</h2>
              {personal.daily_tasks.map((t) => (
                <div key={t.id} className="flex justify-between text-sm py-2 border-b border-[var(--border-glass)]">
                  <span>{t.title}</span>
                  <span className="text-[var(--text-muted)] capitalize">{t.status}</span>
                </div>
              ))}
            </div>
            <div className="glass-card p-6">
              <h2 className="font-semibold mb-3">Goals</h2>
              {personal.goals.map((g) => (
                <p key={g.id} className="text-sm py-1.5">{g.title}</p>
              ))}
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="font-semibold mb-4">Activity Heatmap</h2>
            <div className="flex flex-wrap gap-1">
              {Object.entries(personal.activity_heatmap).map(([day, count]) => (
                <div
                  key={day}
                  title={`${day}: ${count} events`}
                  className="w-3 h-3 rounded-sm"
                  style={{ backgroundColor: `rgba(79, 110, 247, ${Math.min(count / 5, 1)})` }}
                />
              ))}
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="font-semibold mb-3">Habits</h2>
            <div className="flex flex-wrap gap-2">
              {personal.habits.map((h) => (
                <span key={h.id} className="px-3 py-1 rounded-full text-xs bg-trace-100 dark:bg-trace-900/40 text-trace-700 dark:text-trace-300">
                  {h.name} ({h.frequency})
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </AppShell>
  );
}
