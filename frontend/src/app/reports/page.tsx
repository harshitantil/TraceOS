"use client";

import { useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

const REPORT_TYPES = [
  { id: "daily", label: "Daily Report" },
  { id: "weekly", label: "Weekly Report" },
  { id: "monthly", label: "Monthly Report" },
  { id: "project", label: "Project Report" },
  { id: "company", label: "Company Report" },
  { id: "risk", label: "Risk Report" },
];

export default function ReportsPage() {
  const [report, setReport] = useState<{ title: string; content: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const generate = async (type: string) => {
    setLoading(true);
    try {
      const res = await api.report(type);
      setReport(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">Reports</h1>
      <div className="flex flex-wrap gap-3 mb-8">
        {REPORT_TYPES.map((r) => (
          <button
            key={r.id}
            onClick={() => generate(r.id)}
            disabled={loading}
            className="bg-white border border-slate-200 px-4 py-2 rounded-lg text-sm hover:border-trace-500"
          >
            {r.label}
          </button>
        ))}
      </div>
      {report && (
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">{report.title}</h2>
          <pre className="text-sm text-slate-700 whitespace-pre-wrap font-sans">{report.content}</pre>
        </div>
      )}
    </AppShell>
  );
}
