"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { api, EntityHub } from "@/lib/api";
import FileUpload from "./FileUpload";

const TABS = ["Overview", "Activity", "Files", "Comments", "Timeline", "Relationships"] as const;

const API_PATHS: Record<string, string> = {
  project: "projects",
  task: "tasks",
  meeting: "meetings",
  decision: "decisions",
  client: "clients",
  document: "documents",
};

interface EntityDetailProps {
  entityType: string;
  entityId: string;
  titleField?: string;
}

export default function EntityDetail({ entityType, entityId, titleField = "title" }: EntityDetailProps) {
  const [hub, setHub] = useState<EntityHub | null>(null);
  const [tab, setTab] = useState<typeof TABS[number]>("Overview");
  const [comment, setComment] = useState("");
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.hub(entityType, entityId);
      setHub(data);
      setForm(data.entity);
      setHasUnsavedChanges(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load entity");
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { load(); }, [entityType, entityId]);

  const save = async () => {
    const path = API_PATHS[entityType];
    if (!path) return;
    setLoading(true);
    setError("");
    try {
      const payload = { ...form };
      delete payload.id;
      delete payload.organization_id;
      delete payload.created_at;
      delete payload.updated_at;
      delete payload.deleted_at;
      await api.update(`/${path}/${entityId}`, payload);
      setEditMode(false);
      setHasUnsavedChanges(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save entity");
    } finally {
      setLoading(false);
    }
  };

  const postComment = async () => {
    if (!comment.trim()) return;
    try {
      await api.addComment(entityType, entityId, comment);
      setComment("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to post comment");
    }
  };

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [hasUnsavedChanges]);

  if (!hub) return <div className="animate-pulse text-[var(--text-muted)]">Loading...</div>;

  const title = String(hub.entity[titleField] || hub.entity.name || "Untitled");

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="max-w-5xl">
      {error && (
        <div className="mb-4 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-sm rounded-lg px-4 py-3">
          {error}
        </div>
      )}
      {saveSuccess && (
        <div className="mb-4 bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 text-sm rounded-lg px-4 py-3">
          Saved successfully
        </div>
      )}
      <div className="mb-6">
        <Link href={`/${API_PATHS[entityType] || entityType}`} className="text-sm text-trace-600 hover:underline capitalize">
          ← Back to {entityType}s
        </Link>
        <div className="flex items-center justify-between mt-2">
          <h1 className="text-3xl font-bold">{title}</h1>
          <button
            onClick={() => {
              if (hasUnsavedChanges && !confirm("You have unsaved changes. Are you sure you want to cancel?")) return;
              setEditMode(!editMode);
              setForm(hub.entity);
              setHasUnsavedChanges(false);
            }}
            className="px-4 py-2 text-sm glass-card hover:bg-trace-50 dark:hover:bg-trace-900/30"
            disabled={loading}
          >
            {editMode ? "Cancel" : "Edit"}
          </button>
        </div>
      </div>

      <div className="flex gap-1 mb-6 overflow-x-auto">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-colors ${
              tab === t ? "bg-trace-600 text-white" : "text-[var(--text-muted)] hover:bg-[var(--bg-glass)]"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="glass-card p-6">
        {tab === "Overview" && (
          editMode ? (
            <div className="space-y-4">
              {Object.entries(form).filter(([k]) => !["id", "organization_id", "created_at", "updated_at", "deleted_at"].includes(k)).map(([key, val]) => (
                <div key={key}>
                  <label className="text-xs font-medium text-[var(--text-muted)] uppercase">{key.replace(/_/g, " ")}</label>
                  {typeof val === "string" && val.length > 100 ? (
                    <textarea
                      value={String(val)}
                      onChange={(e) => { setForm({ ...form, [key]: e.target.value }); setHasUnsavedChanges(true); }}
                      className="w-full mt-1 border border-[var(--border-glass)] rounded-lg px-3 py-2 bg-transparent"
                      rows={3}
                    />
                  ) : (
                    <input
                      value={String(val ?? "")}
                      onChange={(e) => { setForm({ ...form, [key]: e.target.value }); setHasUnsavedChanges(true); }}
                      className="w-full mt-1 border border-[var(--border-glass)] rounded-lg px-3 py-2 bg-transparent"
                    />
                  )}
                </div>
              ))}
              <button onClick={save} disabled={loading} className="px-4 py-2 bg-trace-600 text-white rounded-lg text-sm disabled:opacity-50">
                {loading ? "Saving..." : "Save"}
              </button>
            </div>
          ) : (
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(hub.entity).filter(([k]) => !["id", "organization_id", "created_at", "updated_at", "deleted_at"].includes(k)).map(([key, val]) => (
                <div key={key}>
                  <dt className="text-xs font-medium text-[var(--text-muted)] uppercase">{key.replace(/_/g, " ")}</dt>
                  <dd className="mt-1 text-sm">{String(val ?? "—")}</dd>
                </div>
              ))}
            </dl>
          )
        )}

        {tab === "Activity" && (
          <div className="space-y-3">
            {hub.activity.map((a) => (
              <div key={a.id} className="flex justify-between text-sm py-2 border-b border-[var(--border-glass)]">
                <span className="capitalize">{a.action}</span>
                <span className="text-[var(--text-muted)]">{new Date(a.created_at).toLocaleString()}</span>
              </div>
            ))}
            {hub.activity.length === 0 && <p className="text-[var(--text-muted)] text-sm">No activity yet.</p>}
          </div>
        )}

        {tab === "Files" && (
          <div>
            {hub.files.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-[var(--text-muted)]">No files uploaded yet</p>
                <p className="text-sm text-[var(--text-muted)] mt-1">Upload files to attach them to this entity</p>
              </div>
            ) : (
              <FileUpload entityType={entityType} entityId={entityId} files={hub.files} onUploaded={load} />
            )}
          </div>
        )}

        {tab === "Comments" && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <input
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Add a comment..."
                className="flex-1 border border-[var(--border-glass)] rounded-lg px-3 py-2 bg-transparent"
                onKeyDown={(e) => e.key === "Enter" && postComment()}
              />
              <button onClick={postComment} className="px-4 py-2 bg-trace-600 text-white rounded-lg text-sm">Post</button>
            </div>
            {hub.comments.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-[var(--text-muted)]">No comments yet</p>
                <p className="text-sm text-[var(--text-muted)] mt-1">Be the first to comment on this entity</p>
              </div>
            ) : (
              hub.comments.map((c) => (
                <div key={c.id} className="p-3 rounded-lg bg-[var(--bg-glass)]">
                  <p className="text-sm">{c.content}</p>
                  <p className="text-xs text-[var(--text-muted)] mt-1">{new Date(c.created_at).toLocaleString()}</p>
                </div>
              ))
            )}
          </div>
        )}

        {tab === "Timeline" && (
          <div>
            {hub.timeline.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-[var(--text-muted)]">No timeline events yet</p>
                <p className="text-sm text-[var(--text-muted)] mt-1">Timeline events will appear here as activity happens</p>
              </div>
            ) : (
              <div className="border-l-2 border-trace-300 ml-2 space-y-4">
                {hub.timeline.map((e) => (
                  <div key={e.id} className="relative pl-6">
                    <div className="absolute -left-[5px] top-1 w-2.5 h-2.5 rounded-full bg-trace-500" />
                    <p className="font-medium text-sm">{e.title}</p>
                    <p className="text-xs text-[var(--text-muted)]">{e.event_type} · {new Date(e.timestamp).toLocaleString()}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === "Relationships" && (
          <div className="space-y-2">
            {hub.relationships.map((r, i) => (
              <Link
                key={i}
                href={`/entities/${r.type}/${r.id}`}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-[var(--bg-glass)] transition-colors"
              >
                <span className="text-xs bg-trace-100 dark:bg-trace-900/40 text-trace-700 dark:text-trace-300 px-2 py-0.5 rounded capitalize">{r.type}</span>
                <span className="text-sm font-medium">{r.label}</span>
                <span className="text-xs text-[var(--text-muted)] ml-auto">{r.relation}</span>
              </Link>
            ))}
            {hub.relationships.length === 0 && <p className="text-[var(--text-muted)] text-sm">No relationships linked yet.</p>}
          </div>
        )}
      </div>
    </motion.div>
  );
}
