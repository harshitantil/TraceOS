"use client";

import AppShell from "@/components/AppShell";
import EntityList from "@/components/EntityList";

export default function PersonalPage() {
  return (
    <AppShell>
      <div className="space-y-12">
        <EntityList
          title="Journal"
          endpoint="/journal"
          displayKey="content"
          fields={[
            { key: "content", label: "Entry", type: "textarea" },
            { key: "date", label: "Date", type: "date" },
          ]}
        />
        <EntityList
          title="Goals"
          endpoint="/goals"
          displayKey="title"
          fields={[
            { key: "title", label: "Goal" },
            { key: "target_date", label: "Target Date", type: "date" },
          ]}
        />
        <EntityList
          title="Ideas"
          endpoint="/ideas"
          displayKey="title"
          fields={[
            { key: "title", label: "Idea" },
            { key: "content", label: "Details", type: "textarea" },
          ]}
        />
        <EntityList
          title="Habits"
          endpoint="/habits"
          displayKey="name"
          fields={[
            { key: "name", label: "Habit" },
            { key: "frequency", label: "Frequency" },
          ]}
        />
      </div>
    </AppShell>
  );
}
