"use client";

import dynamic from "next/dynamic";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from "recharts";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

interface BlockProps {
  blockType: string;
  data: Record<string, unknown>;
  onChange: (data: Record<string, unknown>) => void;
}

export default function BlockRenderer({ blockType, data, onChange }: BlockProps) {
  switch (blockType) {
    case "text":
      return (
        <textarea
          value={(data.content as string) || ""}
          onChange={(e) => onChange({ ...data, content: e.target.value })}
          placeholder="Start writing..."
          className="w-full min-h-[100px] bg-transparent border-none outline-none resize-y text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
        />
      );

    case "heading":
      return (
        <input
          type="text"
          value={(data.text as string) || ""}
          onChange={(e) => onChange({ ...data, text: e.target.value })}
          className={`w-full bg-transparent border-none outline-none font-bold text-[var(--text-primary)] ${
            (data.level as number) === 1 ? "text-3xl" : (data.level as number) === 3 ? "text-lg" : "text-2xl"
          }`}
          placeholder="Heading"
        />
      );

    case "checklist": {
      const items = (data.items as Array<{ text: string; checked: boolean }>) || [];
      return (
        <div className="space-y-2">
          {items.map((item, i) => (
            <label key={i} className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={item.checked}
                onChange={() => {
                  const updated = [...items];
                  updated[i] = { ...item, checked: !item.checked };
                  onChange({ ...data, items: updated });
                }}
                className="w-4 h-4 rounded border-slate-300 text-trace-600"
              />
              <input
                value={item.text}
                onChange={(e) => {
                  const updated = [...items];
                  updated[i] = { ...item, text: e.target.value };
                  onChange({ ...data, items: updated });
                }}
                className={`flex-1 bg-transparent border-none outline-none ${item.checked ? "line-through text-[var(--text-muted)]" : ""}`}
              />
            </label>
          ))}
          <button
            type="button"
            onClick={() => onChange({ ...data, items: [...items, { text: "New item", checked: false }] })}
            className="text-sm text-trace-600 hover:text-trace-700"
          >
            + Add item
          </button>
        </div>
      );
    }

    case "code":
      return (
        <div className="rounded-lg overflow-hidden border border-[var(--border-glass)]">
          <div className="px-3 py-1.5 bg-slate-800 text-xs text-slate-400 flex items-center gap-2">
            <select
              value={(data.language as string) || "python"}
              onChange={(e) => onChange({ ...data, language: e.target.value })}
              className="bg-transparent border-none outline-none"
            >
              {["python", "javascript", "typescript", "sql", "json"].map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>
          <MonacoEditor
            height="200px"
            language={(data.language as string) || "python"}
            theme="vs-dark"
            value={(data.code as string) || ""}
            onChange={(v) => onChange({ ...data, code: v || "" })}
            options={{ minimap: { enabled: false }, fontSize: 13, padding: { top: 8 } }}
          />
        </div>
      );

    case "table": {
      const rows = (data.rows as string[][]) || [["", ""], ["", ""]];
      return (
        <table className="w-full border-collapse">
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri}>
                {row.map((cell, ci) => (
                  <td key={ci} className="border border-[var(--border-glass)] p-1">
                    <input
                      value={cell}
                      onChange={(e) => {
                        const updated = rows.map((r) => [...r]);
                        updated[ri][ci] = e.target.value;
                        onChange({ ...data, rows: updated });
                      }}
                      className="w-full bg-transparent border-none outline-none px-2 py-1 text-sm"
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
    }

    case "task":
      return (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-trace-50/50 dark:bg-trace-900/20">
          <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center text-green-600 text-sm">✓</div>
          <input
            value={(data.title as string) || ""}
            onChange={(e) => onChange({ ...data, title: e.target.value })}
            placeholder="Task title"
            className="flex-1 bg-transparent border-none outline-none font-medium"
          />
        </div>
      );

    case "decision":
      return (
        <div className="p-4 rounded-lg bg-orange-50/50 dark:bg-orange-900/10 border-l-4 border-orange-500">
          <input
            value={(data.title as string) || ""}
            onChange={(e) => onChange({ ...data, title: e.target.value })}
            placeholder="Decision"
            className="w-full bg-transparent border-none outline-none font-semibold mb-2"
          />
          <textarea
            value={(data.reason as string) || ""}
            onChange={(e) => onChange({ ...data, reason: e.target.value })}
            placeholder="Reason for this decision..."
            className="w-full bg-transparent border-none outline-none text-sm text-[var(--text-muted)] resize-none"
            rows={2}
          />
        </div>
      );

    case "meeting":
      return (
        <div className="p-4 rounded-lg bg-purple-50/50 dark:bg-purple-900/10 border-l-4 border-purple-500">
          <input
            value={(data.title as string) || ""}
            onChange={(e) => onChange({ ...data, title: e.target.value })}
            placeholder="Meeting title"
            className="w-full bg-transparent border-none outline-none font-semibold mb-2"
          />
          <textarea
            value={(data.notes as string) || ""}
            onChange={(e) => onChange({ ...data, notes: e.target.value })}
            placeholder="Meeting notes..."
            className="w-full bg-transparent border-none outline-none text-sm resize-none"
            rows={3}
          />
        </div>
      );

    case "timeline": {
      const events = (data.events as Array<{ title: string; date: string }>) || [];
      return (
        <div className="border-l-2 border-trace-300 pl-4 space-y-3">
          {events.map((ev, i) => (
            <div key={i} className="relative">
              <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-trace-500" />
              <input
                value={ev.title}
                onChange={(e) => {
                  const updated = [...events];
                  updated[i] = { ...ev, title: e.target.value };
                  onChange({ ...data, events: updated });
                }}
                className="w-full bg-transparent border-none outline-none font-medium text-sm"
              />
            </div>
          ))}
          <button
            type="button"
            onClick={() => onChange({ ...data, events: [...events, { title: "New event", date: new Date().toISOString() }] })}
            className="text-sm text-trace-600"
          >
            + Add event
          </button>
        </div>
      );
    }

    case "chart": {
      const chartData = (data.values as Array<{ name: string; value: number }>) || [
        { name: "Jan", value: 10 }, { name: "Feb", value: 20 }, { name: "Mar", value: 15 },
      ];
      return (
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Bar dataKey="value" fill="#4f6ef7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    }

    default:
      return (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border-l-4 border-red-500">
          <p className="text-sm font-medium text-red-600 dark:text-red-400">Unknown block type: {blockType}</p>
          <p className="text-xs text-red-500 dark:text-red-300 mt-1">This block type is not supported yet. Please contact support or use a different block type.</p>
        </div>
      );
  }
}
