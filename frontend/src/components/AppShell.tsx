"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { Moon, Sun, Command } from "lucide-react";
import Sidebar from "./Sidebar";
import CommandPalette from "./CommandPalette";
import AIAssistant from "./AIAssistant";
import { api, clearToken, getToken } from "@/lib/api";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);
  const [cmdOpen, setCmdOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!getToken()) {
      router.push("/login");
      return;
    }
    api.me().then(setUser).catch(() => {
      clearToken();
      router.push("/login");
    });
  }, [router]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-trace-600">Loading TraceOS...</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="glass sticky top-0 z-30 px-4 md:px-8 py-3 flex justify-between items-center">
          <button
            onClick={() => setCmdOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm text-[var(--text-muted)] hover:bg-[var(--bg-glass)] border border-[var(--border-glass)]"
          >
            <Command size={14} />
            <span className="hidden sm:inline">Command Center</span>
            <kbd className="hidden md:inline text-xs bg-[var(--bg-glass)] px-1.5 py-0.5 rounded ml-2">⌘K</kbd>
          </button>
          <div className="flex items-center gap-3">
            {mounted && (
              <button
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="p-2 rounded-lg hover:bg-[var(--bg-glass)] text-[var(--text-muted)]"
              >
                {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            )}
            <span className="text-sm text-[var(--text-muted)] hidden sm:inline">{user.name}</span>
            <button
              onClick={() => { clearToken(); router.push("/login"); }}
              className="text-sm text-trace-600 hover:text-trace-700"
            >
              Sign out
            </button>
          </div>
        </header>
        <main className="flex-1 p-4 md:p-8 overflow-auto">{children}</main>
      </div>
      <CommandPalette open={cmdOpen} onOpenChange={setCmdOpen} />
      <AIAssistant />
    </div>
  );
}
