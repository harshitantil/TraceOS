const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("traceos_token");
}

export function setToken(token: string) {
  localStorage.setItem("traceos_token", token);
}

export function clearToken() {
  localStorage.removeItem("traceos_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : "Request failed");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  register: (data: { name: string; email: string; password: string; organization_name: string }) =>
    request<{ access_token: string }>("/api/v1/auth/register", { method: "POST", body: JSON.stringify(data) }),

  login: (data: { email: string; password: string }) =>
    request<{ access_token: string }>("/api/v1/auth/login", { method: "POST", body: JSON.stringify(data) }),

  me: () => request<{ id: string; name: string; email: string; role: string }>("/api/v1/auth/me"),

  list: <T>(path: string) => request<T[]>(`/api/v1${path}`),
  get: <T>(path: string) => request<T>(`/api/v1${path}`),
  create: <T>(path: string, data: unknown) =>
    request<T>(`/api/v1${path}`, { method: "POST", body: JSON.stringify(data) }),
  update: <T>(path: string, data: unknown) =>
    request<T>(`/api/v1${path}`, { method: "PATCH", body: JSON.stringify(data) }),

  hub: (entityType: string, entityId: string) =>
    request<EntityHub>(`/api/v1/entities/${entityType}/${entityId}/hub`),

  addComment: (entityType: string, entityId: string, content: string) =>
    request(`/api/v1/entities/${entityType}/${entityId}/comments`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  uploadFile: (entityType: string, entityId: string, file: File) => {
    const form = new FormData();
    form.append("entity_type", entityType);
    form.append("entity_id", entityId);
    form.append("file", file);
    return request<FileMeta>("/api/v1/files/upload", { method: "POST", body: form });
  },

  fileUrl: (fileId: string) => `${API_URL}/api/v1/files/${fileId}/download`,

  search: (query: string, search_type = "semantic") =>
    request<SearchResult[]>("/api/v1/search", { method: "POST", body: JSON.stringify({ query, search_type }) }),

  chat: (question: string) =>
    request<{ answer: string; sources: Array<{ entity_type: string; title: string }> }>(
      "/api/v1/ai/chat",
      { method: "POST", body: JSON.stringify({ question }) }
    ),

  digest: () => request<DailyDigest>("/api/v1/ai/digest"),
  replay: (start: string, end?: string) =>
    request<ActivityReplay>(`/api/v1/ai/replay?start_date=${start}${end ? `&end_date=${end}` : ""}`),
  categorize: (content: string) =>
    request<{ category: string; confidence: number }>("/api/v1/ai/categorize", {
      method: "POST",
      body: JSON.stringify({ question: content }),
    }),

  report: (report_type: string) =>
    request<{ title: string; content: string; report_type: string }>(
      "/api/v1/reports",
      { method: "POST", body: JSON.stringify({ report_type }) }
    ),

  timeline: (view = "weekly") =>
    request<TimelineEvent[]>(`/api/v1/timeline?view=${view}`),

  graph: () => request<GraphData>("/api/v1/graph"),

  founderDashboard: () => request<FounderDashboard>("/api/v1/dashboard/founder"),
  personalDashboard: () => request<PersonalDashboard>("/api/v1/dashboard/personal"),
  projectHealth: () => request<ProjectHealth[]>("/api/v1/dashboard/project-health"),

  journeys: () => request<Journey[]>("/api/v1/journeys"),
  createJourney: (data: { title: string; description?: string; steps?: unknown[] }) =>
    request("/api/v1/journeys", { method: "POST", body: JSON.stringify(data) }),
};

export interface SearchResult {
  entity_type: string;
  entity_id: string;
  title: string;
  content: string;
  score: number;
}

export interface EntityHub {
  entity_type: string;
  entity: Record<string, unknown>;
  timeline: Array<{ id: string; title: string; event_type: string; timestamp: string }>;
  activity: Array<{ id: string; action: string; created_at: string }>;
  comments: Array<{ id: string; content: string; user_id: string; created_at: string }>;
  files: FileMeta[];
  relationships: Array<{ type: string; id: string; label: string; relation: string }>;
}

export interface FileMeta {
  id: string;
  filename: string;
  mime_type: string;
  size: number;
  version: number;
  created_at: string;
}

export interface TimelineEvent {
  id: string;
  title: string;
  entity_type: string;
  timestamp: string;
  event_type: string;
}

export interface GraphData {
  nodes: Array<{ id: string; type: string; label: string; reference_id: string }>;
  edges: Array<{ id: string; source_node: string; target_node: string; relation_type: string }>;
}

export interface FounderDashboard {
  active_projects: Array<{ id: string; name: string; status: string }>;
  revenue_total: number;
  monthly_revenue: Array<{ month: string; total: number }>;
  risks: Array<{ id: string; title: string; due_date: string | null }>;
  team_activity: Array<{ title: string; entity_type: string; timestamp: string }>;
  ai_summary: string;
  stats: { projects: number; tasks: number; overdue_tasks: number };
}

export interface PersonalDashboard {
  daily_tasks: Array<{ id: string; title: string; status: string }>;
  goals: Array<{ id: string; title: string; target_date: string | null }>;
  habits: Array<{ id: string; name: string; frequency: string }>;
  recent_notes: Array<{ content: string; date: string }>;
  activity_heatmap: Record<string, number>;
  timeline: Array<{ title: string; entity_type: string; timestamp: string }>;
}

export interface ProjectHealth {
  id: string;
  name: string;
  progress: number;
  overdue: number;
  status: "green" | "yellow" | "red";
}

export interface Journey {
  id: string;
  title: string;
  description?: string;
  status: string;
  steps: Array<{ id: string; entity_type: string; entity_id: string; label: string; step_order: number }>;
}

export interface DailyDigest {
  date: string;
  pending_work: Array<{ title: string; status: string }>;
  blocked_tasks: Array<{ title: string }>;
  overdue_tasks: Array<{ title: string; due_date: string }>;
  meetings_today: Array<{ title: string; time: string }>;
  risks: number;
  ai_summary: string;
}

export interface ActivityReplay {
  start: string;
  end: string;
  events: Array<{ title: string; entity_type: string; event_type: string; timestamp: string }>;
  total: number;
}
