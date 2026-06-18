"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send } from "lucide-react";
import { api } from "@/lib/api";

export default function AIAssistant() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Array<{ role: "user" | "ai"; text: string }>>([]);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    if (!question.trim() || loading) return;
    const q = question;
    setQuestion("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const res = await api.chat(q);
      setMessages((m) => [...m, { role: "ai", text: res.answer }]);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to get response";
      console.error("AI chat error:", err);
      setMessages((m) => [...m, { role: "ai", text: `Error: ${errorMsg}. Please check your API key configuration or try again.` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-trace-600 text-white shadow-lg shadow-trace-600/30 flex items-center justify-center hover:bg-trace-700 transition-colors"
      >
        <MessageCircle size={24} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-40 w-96 max-h-[500px] glass-card shadow-2xl flex flex-col"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-glass)]">
              <span className="font-semibold text-sm">AI Assistant</span>
              <button onClick={() => setOpen(false)} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                <X size={18} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[200px] max-h-[340px]">
              {messages.length === 0 && (
                <p className="text-sm text-[var(--text-muted)]">Ask about your company history, decisions, or projects.</p>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`text-sm p-3 rounded-lg ${m.role === "user" ? "bg-trace-600 text-white ml-8" : "bg-[var(--bg-glass)] mr-8"}`}>
                  {m.text}
                </div>
              ))}
              {loading && <div className="text-sm text-[var(--text-muted)] animate-pulse">Thinking...</div>}
            </div>
            <div className="p-3 border-t border-[var(--border-glass)] flex gap-2">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && ask()}
                placeholder="Ask anything..."
                className="flex-1 bg-transparent border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm outline-none"
              />
              <button onClick={ask} disabled={loading} className="p-2 bg-trace-600 text-white rounded-lg">
                <Send size={16} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
