"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";
import Link from "next/link";

export default function PagesListPage() {
  const [pages, setPages] = useState<Array<{ id: string; title: string }>>([]);
  const [title, setTitle] = useState("");

  const load = () => api.list<{ id: string; title: string }>("/pages").then(setPages);
  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    const page = await api.create<{ id: string }>("/pages", { title });
    setTitle("");
    window.location.href = `/pages/${page.id}`;
  };

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">Pages</h1>
      <form onSubmit={create} className="flex gap-3 mb-6">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New page title"
          className="flex-1 border border-slate-200 rounded-lg px-3 py-2"
          required
        />
        <button type="submit" className="bg-trace-600 text-white px-4 py-2 rounded-lg">Create</button>
      </form>
      <div className="space-y-2">
        {pages.map((p) => (
          <Link key={p.id} href={`/pages/${p.id}`} className="block bg-white border border-slate-200 rounded-lg p-4 hover:border-trace-500">
            {p.title}
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
