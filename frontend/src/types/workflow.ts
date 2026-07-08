export type DisplaySection = {
  heading: string;
  type: string;
  content?: string;
  items?: string[];
  rows?: Record<string, unknown> | unknown[];
  scores?: Array<Record<string, unknown>>;
  diagrams?: Array<{ title: string; code: string }>;
};

export type DisplayData = {
  title: string;
  subtitle?: string;
  sections: DisplaySection[];
};

export type WorkflowStage =
  | "discovery"
  | "knowledge"
  | "recommendation"
  | "architecture"
  | "validation"
  | "output";

export type WorkflowRequest = {
  stage: WorkflowStage;
  action: "start" | "edit" | "approve" | "instruction";
  requirement?: string;
  instruction?: string;
  agent_data?: Record<string, unknown>;
  discovery_agent_data?: Record<string, unknown>;
  workflow_context?: WorkflowContext;
};

export type WorkflowResponse = {
  status: string;
  stage: WorkflowStage;
  display_data: DisplayData;
  agent_data: Record<string, unknown>;
  next_actions: string[];
};

export type UploadResponse = {
  filename: string;
  file_type: string;
  text: string;
};

export type WorkflowContext = Partial<Record<WorkflowStage, Record<string, unknown>>>;
