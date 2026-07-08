import axios from "axios";

import type { UploadResponse, WorkflowRequest, WorkflowResponse } from "@/types/workflow";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
});

export async function sendWorkflowInstruction(payload: WorkflowRequest) {
  const response = await api.post<WorkflowResponse>("/workflow", payload);
  return response.data;
}

export async function uploadRequirement(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<UploadResponse>("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}
