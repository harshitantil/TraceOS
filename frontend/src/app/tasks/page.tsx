"use client";

import AppShell from "@/components/AppShell";
import EntityList from "@/components/EntityList";

export default function TasksPage() {
  return (
    <AppShell>
      <EntityList
        title="Tasks"
        endpoint="/tasks"
        entityType="task"
        displayKey="title"
        fields={[
          { key: "title", label: "Title" },
          { key: "status", label: "Status" },
          { key: "due_date", label: "Due Date", type: "date" },
        ]}
      />
    </AppShell>
  );
}
