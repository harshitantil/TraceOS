"use client";

import AppShell from "@/components/AppShell";
import EntityList from "@/components/EntityList";

export default function ProjectsPage() {
  return (
    <AppShell>
      <EntityList
        title="Projects"
        endpoint="/projects"
        entityType="project"
        displayKey="name"
        fields={[
          { key: "name", label: "Name" },
          { key: "description", label: "Description", type: "textarea" },
          { key: "status", label: "Status" },
        ]}
      />
    </AppShell>
  );
}
