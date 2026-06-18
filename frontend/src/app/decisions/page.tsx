"use client";

import AppShell from "@/components/AppShell";
import EntityList from "@/components/EntityList";

export default function DecisionsPage() {
  return (
    <AppShell>
      <EntityList
        title="Decisions"
        endpoint="/decisions"
        entityType="decision"
        displayKey="title"
        fields={[
          { key: "title", label: "Decision" },
          { key: "reason", label: "Reason", type: "textarea" },
          { key: "expected_outcome", label: "Expected Outcome", type: "textarea" },
        ]}
      />
    </AppShell>
  );
}
