import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { Section } from "@/components/common/Section";
import { useWorkflow } from "@/hooks/useWorkflow";

export function UploadPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { uploadAndStart, isLoading, error, loadingMessage } = useWorkflow();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  async function handleStartWorkflow() {
    if (!selectedFile) {
      inputRef.current?.click();
      return;
    }

    await uploadAndStart(selectedFile);
    navigate("/workspace");
  }

  return (
    <Section
      title="Upload"
      description="Upload a PDF, DOCX, or TXT requirement document to start the AI workflow."
    >
      <Card className="p-6">
        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <button
            type="button"
            className="flex min-h-72 flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 px-6 text-center transition-colors hover:border-primary hover:bg-blue-50"
            onClick={() => inputRef.current?.click()}
          >
            <UploadCloud className="mb-4 h-10 w-10 text-primary" />
            <h3 className="text-base font-semibold text-slate-950">
              {selectedFile ? selectedFile.name : "Choose requirement document"}
            </h3>
            <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
              Supported formats: PDF, DOCX, and TXT. The backend extracts text, then the workflow
              starts with Discovery.
            </p>
          </button>

          <div className="flex flex-col justify-between rounded-lg border border-slate-200 bg-white p-5">
            <div>
              <h3 className="text-sm font-semibold text-slate-950">Workflow Start</h3>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Upload sends the file to <span className="font-medium text-slate-700">/upload</span>,
                then starts <span className="font-medium text-slate-700">/workflow</span>.
              </p>

              {error ? (
                <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {error}
                </div>
              ) : null}

              {isLoading ? (
                <div className="mt-4 rounded-md border border-blue-100 bg-blue-50 p-3 text-sm text-blue-800">
                  {loadingMessage}
                </div>
              ) : null}
            </div>

            <Button className="mt-6 w-full" disabled={isLoading} onClick={handleStartWorkflow}>
              {selectedFile ? "Start AI Workflow" : "Select File"}
            </Button>
          </div>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
          className="hidden"
          onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
        />
      </Card>
    </Section>
  );
}
