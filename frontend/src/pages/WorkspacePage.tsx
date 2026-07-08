import { Button } from "@/components/common/Button";
import { DocumentViewer } from "@/components/document/DocumentViewer";
import { OutputWorkspace } from "@/components/workflow/OutputWorkspace";
import { AIInstructionPanel } from "@/components/workflow/AIInstructionPanel";
import { WorkflowTimeline } from "@/components/workflow/WorkflowTimeline";
import { Loading } from "@/components/common/Loading";
import { useWorkflow } from "@/hooks/useWorkflow";

export function WorkspacePage() {
  const {
    currentStage,
    displayData,
    isLoading,
    error,
    loadingMessage,
    sendInstruction,
    retryLastInstruction,
  } = useWorkflow();

  return (
    <div className="relative -mb-6 min-h-[calc(100vh-8rem)] pb-40">
      <div className="sticky top-0 z-10 -mx-4 bg-background/95 px-4 pb-4 backdrop-blur sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
        <WorkflowTimeline currentStep={currentStage} />
      </div>

      <div className="mt-5 space-y-4">
        <div>
          {isLoading ? (
            <Loading message={loadingMessage} />
          ) : (
            <div className="rounded-lg border border-slate-100 bg-white/60 px-4 py-3 text-sm text-slate-700">Review the document, then provide instructions below.</div>
          )}
        </div>

        {error ? (
          <div className="flex flex-col gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 sm:flex-row sm:items-center sm:justify-between">
            <span>{error}</span>
            <Button variant="secondary" disabled={isLoading} onClick={retryLastInstruction}>
              Retry
            </Button>
          </div>
        ) : null}

        {currentStage === "output" ? (
          <OutputWorkspace displayData={displayData} />
        ) : (
          <DocumentViewer displayData={displayData} />
        )}
      </div>

      <AIInstructionPanel isSending={isLoading} onSend={sendInstruction} />
    </div>
  );
}
