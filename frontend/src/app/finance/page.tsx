"use client";

import AppShell from "@/components/AppShell";
import EntityList from "@/components/EntityList";

export default function FinancePage() {
  return (
    <AppShell>
      <div className="space-y-12">
        <EntityList
          title="Revenue"
          endpoint="/revenues"
          displayKey="amount"
          fields={[
            { key: "amount", label: "Amount", type: "number" },
            { key: "date", label: "Date", type: "date" },
            { key: "description", label: "Description" },
          ]}
        />
        <EntityList
          title="Expenses"
          endpoint="/expenses"
          displayKey="amount"
          fields={[
            { key: "amount", label: "Amount", type: "number" },
            { key: "category", label: "Category" },
            { key: "date", label: "Date", type: "date" },
          ]}
        />
      </div>
    </AppShell>
  );
}
