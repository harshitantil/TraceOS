"use client";

import AppShell from "@/components/AppShell";
import EntityList from "@/components/EntityList";

export default function MeetingsPage() {
  return (
    <AppShell>
      <EntityList
        title="Meetings"
        endpoint="/meetings"
        entityType="meeting"
        displayKey="title"
        fields={[
          { key: "title", label: "Title" },
          { key: "date", label: "Date & Time", type: "datetime-local" },
          { key: "notes", label: "Notes", type: "textarea" },
        ]}
      />
    </AppShell>
  );
}
