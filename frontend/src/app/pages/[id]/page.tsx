"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import AppShell from "@/components/AppShell";
import BlockRenderer from "@/components/blocks/BlockRenderer";
import { api } from "@/lib/api";

const BLOCK_TYPES = ["text", "heading", "checklist", "code", "table", "task", "decision", "meeting", "timeline", "chart"];

export default function PageEditor() {
  const { id } = useParams();
  const [page, setPage] = useState<{ title: string } | null>(null);
  const [blocks, setBlocks] = useState<Array<{ id: string; block_type: string; data: Record<string, unknown>; order_index: number }>>([]);
  const [newType, setNewType] = useState("text");

  const load = useCallback(async () => {
    const [p, b] = await Promise.all([
      api.get<{ title: string }>(`/pages/${id}`),
      api.list<typeof blocks[0]>(`/pages/${id}/blocks`),
    ]);
    setPage(p);
    setBlocks(b);
  }, [id]);

  useEffect(() => { if (id) load(); }, [id, load]);

  const updateBlock = async (blockId: string, data: Record<string, unknown>) => {
    await api.update(`/pages/blocks/${blockId}`, { data });
    setBlocks((prev) => prev.map((b) => (b.id === blockId ? { ...b, data } : b)));
  };

  const addBlock = async () => {
    const defaults: Record<string, Record<string, unknown>> = {
      text: { content: "" },
      heading: { text: "New Heading", level: 2 },
      checklist: { items: [{ text: "Item 1", checked: false }] },
      code: { language: "python", code: "" },
      table: { rows: [["Column 1", "Column 2"], ["", ""]] },
      task: { title: "New Task" },
      decision: { title: "New Decision", reason: "" },
      meeting: { title: "New Meeting", notes: "" },
      timeline: { events: [{ title: "Event 1", date: new Date().toISOString() }] },
      chart: { values: [{ name: "Jan", value: 10 }, { name: "Feb", value: 20 }, { name: "Mar", value: 15 }] },
    };
    await api.create(`/pages/${id}/blocks`, {
      block_type: newType,
      data: defaults[newType] || {},
      order_index: blocks.length,
    });
    load();
  };

  if (!page) return <AppShell><p className="text-[var(--text-muted)]">Loading...</p></AppShell>;

  return (
    <AppShell>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-3xl font-bold mb-8">{page.title}</h1>
        <div className="space-y-4 mb-8 max-w-3xl">
          {blocks.map((block, i) => (
            <motion.div
              key={block.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-card p-5"
            >
              <span className="text-[10px] font-semibold text-trace-600 uppercase tracking-wider">{block.block_type}</span>
              <div className="mt-3">
                <BlockRenderer
                  blockType={block.block_type}
                  data={block.data}
                  onChange={(data) => updateBlock(block.id, data)}
                />
              </div>
            </motion.div>
          ))}
        </div>
        <div className="flex gap-3 items-center">
          <select
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
            className="border border-[var(--border-glass)] rounded-lg px-3 py-2 bg-transparent text-sm"
          >
            {BLOCK_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <button onClick={addBlock} className="bg-trace-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-trace-700">
            Add Block
          </button>
        </div>
      </motion.div>
    </AppShell>
  );
}
