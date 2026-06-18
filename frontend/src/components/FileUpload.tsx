"use client";

import { useCallback, useState } from "react";
import { Upload, File, Image, FileText } from "lucide-react";
import { api, FileMeta } from "@/lib/api";

interface FileUploadProps {
  entityType: string;
  entityId: string;
  files: FileMeta[];
  onUploaded: () => void;
}

export default function FileUpload({ entityType, entityId, files, onUploaded }: FileUploadProps) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const upload = useCallback(async (fileList: FileList | File[]) => {
    setUploading(true);
    try {
      for (const file of Array.from(fileList)) {
        await api.uploadFile(entityType, entityId, file);
      }
      onUploaded();
    } finally {
      setUploading(false);
    }
  }, [entityType, entityId, onUploaded]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files.length) upload(e.dataTransfer.files);
  };

  const iconFor = (mime: string) => {
    if (mime.startsWith("image/")) return <Image size={16} className="text-blue-500" />;
    if (mime === "application/pdf") return <FileText size={16} className="text-red-500" />;
    return <File size={16} className="text-slate-500" />;
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
          dragging ? "border-trace-500 bg-trace-50/50 dark:bg-trace-900/20" : "border-[var(--border-glass)]"
        }`}
      >
        <Upload className="mx-auto mb-2 text-[var(--text-muted)]" size={24} />
        <p className="text-sm text-[var(--text-muted)] mb-2">Drag & drop files here</p>
        <label className="inline-block px-4 py-2 bg-trace-600 text-white rounded-lg text-sm cursor-pointer hover:bg-trace-700">
          {uploading ? "Uploading..." : "Browse files"}
          <input
            type="file"
            multiple
            className="hidden"
            onChange={(e) => e.target.files && upload(e.target.files)}
            disabled={uploading}
          />
        </label>
      </div>

      <div className="space-y-2">
        {files.map((f) => (
          <div key={f.id} className="flex items-center gap-3 p-3 glass-card">
            {iconFor(f.mime_type)}
            <div className="flex-1 min-w-0">
              <a
                href={api.fileUrl(f.id)}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium hover:text-trace-600 truncate block"
              >
                {f.filename}
              </a>
              <p className="text-xs text-[var(--text-muted)]">
                v{f.version} · {(f.size / 1024).toFixed(1)} KB
              </p>
            </div>
            {f.mime_type.startsWith("image/") && (
              <img src={api.fileUrl(f.id)} alt={f.filename} className="w-12 h-12 rounded object-cover" />
            )}
          </div>
        ))}
        {files.length === 0 && <p className="text-sm text-[var(--text-muted)]">No files attached yet.</p>}
      </div>
    </div>
  );
}
