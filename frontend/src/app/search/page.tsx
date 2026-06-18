"use client";

import { useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [searchType, setSearchType] = useState("semantic");
  const [results, setResults] = useState<Array<{ entity_type: string; title: string; content: string; score: number }>>([]);
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await api.search(query, searchType);
      setResults(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuestion.trim()) return;
    setLoading(true);
    setError("");
    setChatAnswer("");
    try {
      const res = await api.chat(chatQuestion);
      setChatAnswer(res.answer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "AI chat failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">Search & AI Memory</h1>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="font-semibold mb-3">Global Search</h2>
          <form onSubmit={handleSearch} className="flex gap-2 mb-4">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search your company memory..."
              className="flex-1 border border-slate-200 rounded-lg px-3 py-2"
            />
            <select value={searchType} onChange={(e) => setSearchType(e.target.value)} className="border border-slate-200 rounded-lg px-2">
              <option value="semantic">Semantic</option>
              <option value="keyword">Keyword</option>
            </select>
            <button type="submit" className="bg-trace-600 text-white px-4 py-2 rounded-lg" disabled={loading}>Search</button>
          </form>
          <div className="space-y-2">
            {results.length === 0 && !loading && query && (
              <div className="text-center py-8 text-[var(--text-muted)]">
                <p>No results found for "{query}"</p>
                <p className="text-sm mt-2">Try different keywords or switch to semantic search</p>
              </div>
            )}
            {results.map((r, i) => (
              <div key={i} className="glass-card p-3 hover:bg-[var(--bg-glass)] transition-colors cursor-pointer">
                <div className="flex justify-between">
                  <span className="font-medium text-sm">{r.title}</span>
                  <span className="text-xs text-trace-600 capitalize">{r.entity_type}</span>
                </div>
                <p className="text-xs text-[var(--text-muted)] mt-1 line-clamp-2">{r.content}</p>
                <div className="mt-2 text-xs text-[var(--text-muted)]">Relevance: {Math.round(r.score * 100)}%</div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="font-semibold mb-3">AI Memory Chat</h2>
          <div className="glass-card p-4 mb-4">
            <p className="text-xs text-[var(--text-muted)] mb-2">Ask questions about your company history:</p>
            <div className="flex flex-wrap gap-2 mb-3">
              {["What happened yesterday?", "Decisions about Project Alpha", "Meetings this week"].map((q) => (
                <button
                  key={q}
                  onClick={() => setChatQuestion(q)}
                  className="text-xs px-2 py-1 rounded-full bg-[var(--bg-glass)] hover:bg-trace-100 dark:hover:bg-trace-900/30 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
          <form onSubmit={handleChat} className="mb-4">
            <textarea
              value={chatQuestion}
              onChange={(e) => setChatQuestion(e.target.value)}
              placeholder="What happened yesterday? Why was Feature Y built?"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-2"
              rows={3}
            />
            <button type="submit" className="bg-trace-600 text-white px-4 py-2 rounded-lg" disabled={loading}>Ask AI</button>
          </form>
          {chatAnswer && (
            <div className="glass-card p-4">
              <p className="text-sm text-[var(--text-primary)] whitespace-pre-wrap">{chatAnswer}</p>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
