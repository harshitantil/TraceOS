"use client";

import AppShell from "@/components/AppShell";
import EntityList from "@/components/EntityList";

export default function ClientsPage() {
  return (
    <AppShell>
      <EntityList
        title="Clients"
        endpoint="/clients"
        entityType="client"
        displayKey="name"
        fields={[
          { key: "name", label: "Name" },
          { key: "industry", label: "Industry" },
        ]}
      />
    </AppShell>
  );
}
