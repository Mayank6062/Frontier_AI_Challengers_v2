import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { Section } from "@/components/common/Section";

export function SettingsPage() {
  return (
    <Section title="Settings" description="Placeholder for application preferences.">
      <Card className="p-6">
        <EmptyState
          title="Settings placeholder"
          description="Theme, profile, and workspace preferences will be wired in a later step."
        />
      </Card>
    </Section>
  );
}
