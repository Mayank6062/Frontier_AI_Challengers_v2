import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { Section } from "@/components/common/Section";

export function HistoryPage() {
  return (
    <Section title="History" description="Placeholder for previous architecture sessions.">
      <Card className="p-6">
        <EmptyState
          title="No history yet"
          description="Session history is outside Step F1 and will be added later if needed."
        />
      </Card>
    </Section>
  );
}
