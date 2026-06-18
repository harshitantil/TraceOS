"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Brain, Calendar, CheckSquare, FileText, GitBranch, LayoutDashboard,
  Network, Search, Users, DollarSign, Lightbulb, Target, Route, Play,
} from "lucide-react";
import clsx from "clsx";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/pages", label: "Pages", icon: FileText },
  { href: "/projects", label: "Projects", icon: GitBranch },
  { href: "/tasks", label: "Tasks", icon: CheckSquare },
  { href: "/meetings", label: "Meetings", icon: Calendar },
  { href: "/decisions", label: "Decisions", icon: Brain },
  { href: "/clients", label: "Clients", icon: Users },
  { href: "/finance", label: "Finance", icon: DollarSign },
  { href: "/personal", label: "Personal", icon: Target },
  { href: "/timeline", label: "Timeline", icon: Calendar },
  { href: "/journeys", label: "Journeys", icon: Route },
  { href: "/replay", label: "Activity Replay", icon: Play },
  { href: "/graph", label: "Knowledge Graph", icon: Network },
  { href: "/search", label: "Search & AI", icon: Search },
  { href: "/reports", label: "Reports", icon: Lightbulb },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex w-64 glass border-r border-[var(--border-glass)] min-h-screen flex-col">
      <div className="p-6 border-b border-[var(--border-glass)]">
        <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-trace-600 to-trace-500 bg-clip-text text-transparent">
          TraceOS
        </h1>
        <p className="text-[var(--text-muted)] text-xs mt-1">Operating System</p>
      </div>
      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
        {nav.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              "flex items-center gap-3 px-3 py-2 rounded-xl text-sm transition-all",
              pathname === href || pathname.startsWith(href + "/")
                ? "bg-trace-600 text-white shadow-md shadow-trace-600/20"
                : "text-[var(--text-muted)] hover:bg-[var(--bg-glass)] hover:text-[var(--text-primary)]"
            )}
          >
            <Icon size={18} />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
