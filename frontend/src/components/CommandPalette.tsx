"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import { Search, Plus, FileText, CheckSquare, Calendar, Brain, Users, Sparkles } from "lucide-react";
import { api } from "@/lib/api";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Array<{ entity_type: string; title: string; entity_id: string }>>([]);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        onOpenChange(!open);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [open, onOpenChange]);

  const search = useCallback(async (q: string) => {
    if (q.length < 2) { setResults([]); return; }
    try {
      const res = await api.search(q, "keyword");
      setResults(res);
    } catch { setResults([]); }
  }, []);

  useEffect(() => {
    const t = setTimeout(() => search(query), 300);
    return () => clearTimeout(t);
  }, [query, search]);

  const go = (path: string) => {
    onOpenChange(false);
    setQuery("");
    router.push(path);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => onOpenChange(false)} />
      <div className="absolute top-[20%] left-1/2 -translate-x-1/2 w-full max-w-lg">
        <Command className="glass-card shadow-2xl overflow-hidden" loop>
          <div className="flex items-center gap-2 px-4 border-b border-[var(--border-glass)]">
            <Search size={16} className="text-[var(--text-muted)]" />
            <Command.Input
              value={query}
              onValueChange={setQuery}
              placeholder="Search or type a command..."
              className="flex-1 py-4 bg-transparent border-none outline-none text-sm"
            />
            <kbd className="text-xs text-[var(--text-muted)] bg-[var(--bg-glass)] px-1.5 py-0.5 rounded">ESC</kbd>
          </div>
          <Command.List className="max-h-80 overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-[var(--text-muted)]">No results found.</Command.Empty>

            {!query && (
              <Command.Group heading="Create" className="text-xs text-[var(--text-muted)] px-2 py-1">
                {[
                  { label: "Create Task", icon: CheckSquare, path: "/tasks" },
                  { label: "Create Project", icon: Plus, path: "/projects" },
                  { label: "Create Meeting", icon: Calendar, path: "/meetings" },
                  { label: "Create Decision", icon: Brain, path: "/decisions" },
                  { label: "Create Client", icon: Users, path: "/clients" },
                  { label: "Create Note", icon: FileText, path: "/pages" },
                ].map(({ label, icon: Icon, path }) => (
                  <Command.Item
                    key={label}
                    onSelect={() => go(path)}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-sm hover:bg-[var(--bg-glass)] aria-selected:bg-trace-50 dark:aria-selected:bg-trace-900/30"
                  >
                    <Icon size={16} /> {label}
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {!query && (
              <Command.Group heading="Navigate" className="text-xs text-[var(--text-muted)] px-2 py-1 mt-2">
                {[
                  { label: "Dashboard", path: "/dashboard" },
                  { label: "Search & AI", path: "/search" },
                  { label: "Knowledge Graph", path: "/graph" },
                  { label: "Journeys", path: "/journeys" },
                  { label: "Activity Replay", path: "/replay" },
                ].map(({ label, path }) => (
                  <Command.Item
                    key={label}
                    onSelect={() => go(path)}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-sm hover:bg-[var(--bg-glass)] aria-selected:bg-trace-50"
                  >
                    <Sparkles size={16} /> {label}
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {results.map((r) => (
              <Command.Item
                key={`${r.entity_type}-${r.entity_id}`}
                onSelect={() => go(`/entities/${r.entity_type}/${r.entity_id}`)}
                className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer text-sm hover:bg-[var(--bg-glass)]"
              >
                <span className="text-xs capitalize bg-trace-100 dark:bg-trace-900/40 px-1.5 py-0.5 rounded">{r.entity_type}</span>
                {r.title}
              </Command.Item>
            ))}
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
