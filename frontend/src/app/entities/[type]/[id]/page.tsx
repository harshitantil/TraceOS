"use client";

import { useParams } from "next/navigation";
import AppShell from "@/components/AppShell";
import EntityDetail from "@/components/EntityDetail";

const TITLE_FIELDS: Record<string, string> = {
  project: "name",
  client: "name",
  document: "title",
};

export default function EntityPage() {
  const { type, id } = useParams();
  return (
    <AppShell>
      <EntityDetail
        entityType={String(type)}
        entityId={String(id)}
        titleField={TITLE_FIELDS[String(type)] || "title"}
      />
    </AppShell>
  );
}
