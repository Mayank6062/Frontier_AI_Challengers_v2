import { Navigate, Route, Routes } from "react-router-dom";

import { PageLayout } from "@/components/layout/PageLayout";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { HistoryPage } from "@/pages/HistoryPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { UploadPage } from "@/pages/UploadPage";
import { WorkspacePage } from "@/pages/WorkspacePage";
import { WorkflowProvider } from "@/hooks/useWorkflow";

export default function App() {
  return (
    <WorkflowProvider>
      <PageLayout>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/workspace" element={<WorkspacePage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ErrorBoundary>
      </PageLayout>
    </WorkflowProvider>
  );
}
