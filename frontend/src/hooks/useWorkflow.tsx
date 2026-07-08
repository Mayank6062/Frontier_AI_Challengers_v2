import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

import { sendWorkflowInstruction, uploadRequirement } from "@/services/workflow";
import type {
  DisplayData,
  WorkflowContext,
  WorkflowResponse,
  WorkflowStage,
} from "@/types/workflow";

const initialDisplayData: DisplayData = {
  title: "AI Architecture Workspace",
  subtitle: "Your AI-generated architecture documents will appear here for review.",
  sections: [
    {
      heading: "Document Viewer",
      type: "paragraph",
      content:
        "Upload a requirement document to start the AI workflow. This panel renders display_data only.",
    },
    {
      heading: "Instruction Examples",
      type: "bullet_list",
      items: [
        "Proceed",
        "Continue",
        "Use AWS",
        "Use Azure",
        "Improve Security",
        "Reduce Cost",
        "Use PostgreSQL",
        "Add Kubernetes",
      ],
    },
  ],
};

type WorkflowState = {
  currentStage: WorkflowStage;
  displayData: DisplayData;
  workflowContext: WorkflowContext;
  isLoading: boolean;
  error: string | null;
  loadingMessage: string;
  uploadAndStart: (file: File) => Promise<void>;
  sendInstruction: (instruction: string) => Promise<void>;
  retryLastInstruction: () => Promise<void>;
};

const WorkflowContextValue = createContext<WorkflowState | null>(null);

const loadingMessages: Record<WorkflowStage, string> = {
  discovery: "AI is analyzing requirements...",
  knowledge: "AI is enriching enterprise knowledge...",
  recommendation: "AI is generating recommendations...",
  architecture: "AI is designing architecture...",
  validation: "AI is validating architecture...",
  output: "AI is preparing final deliverables...",
};

function getFriendlyError(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong while connecting to the AI workflow.";
}

type WorkflowProviderProps = {
  children: ReactNode;
};

export function WorkflowProvider({ children }: WorkflowProviderProps) {
  const [currentStage, setCurrentStage] = useState<WorkflowStage>("discovery");
  const [displayData, setDisplayData] = useState<DisplayData>(initialDisplayData);
  const [workflowContext, setWorkflowContext] = useState<WorkflowContext>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastInstruction, setLastInstruction] = useState<string | null>(null);

  function applyWorkflowResponse(response: WorkflowResponse) {
    // Backward-compatible response handling:
    // - Legacy `WorkflowResponse` contains `stage`, `display_data`, `agent_data`.
    // - New orchestrator response may contain `workflow_context`, `display_data`, and no `stage`.
    const stageFromResponse = (response as any).stage ?? (response as any).workflow_context?.current_stage ?? currentStage;
    setCurrentStage(stageFromResponse as WorkflowStage);

    const display = (response as any).display_data ?? (response as any).agent_data ?? initialDisplayData;
    setDisplayData(display);

    // The backend is the source of truth for workflow_context.
    if ((response as any).workflow_context) {
      setWorkflowContext((response as any).workflow_context as WorkflowContext);
    } else {
      setWorkflowContext((previousContext) => ({
        ...previousContext,
        [stageFromResponse]: (response as any).agent_data,
      }));
    }
  }

  async function uploadAndStart(file: File) {
    setIsLoading(true);
    setError(null);

    try {
      const upload = await uploadRequirement(file);
      const response = await sendWorkflowInstruction({
        stage: "discovery",
        action: "start",
        requirement: upload.text,
        workflow_context: {},
      });

      setWorkflowContext({});
      applyWorkflowResponse(response);
    } catch (caughtError) {
      setError(getFriendlyError(caughtError));
      throw caughtError;
    } finally {
      setIsLoading(false);
    }
  }

  async function sendInstruction(instruction: string) {
    setIsLoading(true);
    setError(null);
    setLastInstruction(instruction);

    try {
      const response = await sendWorkflowInstruction({
        stage: currentStage,
        action: "instruction",
        instruction,
        agent_data: workflowContext[currentStage],
        discovery_agent_data: workflowContext.discovery,
        workflow_context: workflowContext,
      });

      applyWorkflowResponse(response);
    } catch (caughtError) {
      setError(getFriendlyError(caughtError));
      throw caughtError;
    } finally {
      setIsLoading(false);
    }
  }

  async function retryLastInstruction() {
    if (!lastInstruction) {
      return;
    }

    await sendInstruction(lastInstruction);
  }

  const value = useMemo(
    () => ({
      currentStage,
      displayData,
      workflowContext,
      isLoading,
      error,
      loadingMessage: loadingMessages[currentStage],
      uploadAndStart,
      sendInstruction,
      retryLastInstruction,
    }),
    [currentStage, displayData, error, isLoading, workflowContext],
  );

  return <WorkflowContextValue.Provider value={value}>{children}</WorkflowContextValue.Provider>;
}

export function useWorkflow() {
  const value = useContext(WorkflowContextValue);

  if (!value) {
    throw new Error("useWorkflow must be used inside WorkflowProvider");
  }

  return value;
}
