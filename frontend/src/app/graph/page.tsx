"use client";

import { useEffect, useState, useMemo } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import { api, GraphData } from "@/lib/api";

export default function GraphPage() {
  const [data, setData] = useState<GraphData>({ nodes: [], edges: [] });

  useEffect(() => { api.graph().then(setData); }, []);

  const nodeMap = useMemo(() => Object.fromEntries(data.nodes.map((n) => [n.id, n])), [data.nodes]);

  const positions = useMemo(() => {
    const pos: Record<string, { x: number; y: number }> = {};
    const types = Array.from(new Set(data.nodes.map((n) => n.type)));
    data.nodes.forEach((n, i) => {
      const typeIdx = types.indexOf(n.type);
      const countOfType = data.nodes.filter((x) => x.type === n.type).length;
      const idxInType = data.nodes.filter((x) => x.type === n.type).indexOf(n);
      pos[n.id] = {
        x: 120 + typeIdx * 180,
        y: 80 + (idxInType / Math.max(countOfType - 1, 1)) * 300,
      };
    });
    return pos;
  }, [data.nodes]);

  const typeColors: Record<string, string> = {
    project: "#4f6ef7", task: "#22c55e", meeting: "#a855f7",
    decision: "#f97316", client: "#06b6d4", document: "#64748b",
  };

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-2">Knowledge Graph</h1>
      <p className="text-[var(--text-muted)] text-sm mb-6">
        {data.nodes.length} nodes · {data.edges.length} relationships
      </p>

      <div className="glass-card p-4 overflow-auto">
        <svg width="100%" height={450} viewBox="0 0 900 450" className="min-w-[600px]">
          {data.edges.map((e) => {
            const s = positions[e.source_node];
            const t = positions[e.target_node];
            if (!s || !t) return null;
            return (
              <g key={e.id}>
                <line x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="var(--text-muted)" strokeOpacity={0.3} strokeWidth={1.5} />
                <text x={(s.x + t.x) / 2} y={(s.y + t.y) / 2 - 4} fontSize={9} fill="var(--text-muted)" textAnchor="middle">
                  {e.relation_type}
                </text>
              </g>
            );
          })}
          {data.nodes.map((n) => {
            const p = positions[n.id];
            if (!p) return null;
            const color = typeColors[n.type] || "#94a3b8";
            return (
              <Link key={n.id} href={`/entities/${n.type}/${n.reference_id}`}>
                <g style={{ cursor: "pointer" }}>
                  <circle cx={p.x} cy={p.y} r={28} fill={color} fillOpacity={0.15} stroke={color} strokeWidth={2} />
                  <text x={p.x} y={p.y + 4} fontSize={10} fill="var(--text-primary)" textAnchor="middle" fontWeight={500}>
                    {n.label.slice(0, 10)}
                  </text>
                  <text x={p.x} y={p.y + 40} fontSize={8} fill={color} textAnchor="middle" className="capitalize">
                    {n.type}
                  </text>
                </g>
              </Link>
            );
          })}
        </svg>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2"
      >
        {data.nodes.map((n) => (
          <Link
            key={n.id}
            href={`/entities/${n.type}/${n.reference_id}`}
            className="glass-card p-3 hover:shadow-md transition-shadow"
          >
            <span className="text-xs capitalize font-medium" style={{ color: typeColors[n.type] }}>{n.type}</span>
            <p className="text-sm mt-0.5 truncate">{n.label}</p>
          </Link>
        ))}
      </motion.div>
    </AppShell>
  );
}
