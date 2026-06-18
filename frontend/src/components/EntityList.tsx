"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { api } from "@/lib/api";

interface Field {
  key: string;
  label: string;
  type?: "text" | "textarea" | "date" | "number" | "datetime-local";
}

interface EntityListProps {
  title: string;
  endpoint: string;
  entityType?: string;
  fields: Field[];
  displayKey: string;
}

export default function EntityList({ title, endpoint, entityType, fields, displayKey }: EntityListProps) {
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [form, setForm] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    api.list<Record<string, unknown>>(endpoint)
      .then(setItems)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [endpoint]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, unknown> = {};
    fields.forEach((f) => {
      const val = form[f.key];
      if (!val) return;
      if (f.type === "number") payload[f.key] = parseFloat(val);
      else payload[f.key] = val;
    });
    try {
      await api.create(endpoint, payload);
      setForm({});
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{title}</h1>

      <form onSubmit={handleCreate} className="glass-card p-6 mb-6">
        <h2 className="text-sm font-semibold text-[var(--text-muted)] mb-4">Create New</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {fields.map((f) => (
            <div key={f.key}>
              <label className="block text-xs font-medium text-[var(--text-muted)] mb-1">{f.label}</label>
              {f.type === "textarea" ? (
                <textarea
                  value={form[f.key] || ""}
                  onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
                  className="w-full border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm bg-transparent"
                  rows={3}
                />
              ) : (
                <input
                  type={f.type || "text"}
                  value={form[f.key] || ""}
                  onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
                  className="w-full border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm bg-transparent"
                />
              )}
            </div>
          ))}
        </div>
        <button type="submit" className="mt-4 bg-trace-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-trace-700">
          Create
        </button>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </form>

      {loading ? (
        <p className="text-[var(--text-muted)]">Loading...</p>
      ) : (
        <div className="space-y-2">
          {items.map((item, i) => (
            <motion.div
              key={String(item.id)}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              {entityType ? (
                <Link
                  href={`/entities/${entityType}/${item.id}`}
                  className="block glass-card p-4 hover:shadow-md transition-shadow"
                >
                  <h3 className="font-medium">{String(item[displayKey])}</h3>
                  <p className="text-xs text-[var(--text-muted)] mt-1 capitalize">{entityType}</p>
                </Link>
              ) : (
                <div className="glass-card p-4">
                  <h3 className="font-medium">{String(item[displayKey])}</h3>
                </div>
              )}
            </motion.div>
          ))}
          {items.length === 0 && <p className="text-[var(--text-muted)]">No items yet.</p>}
        </div>
      )}
    </div>
  );
}
