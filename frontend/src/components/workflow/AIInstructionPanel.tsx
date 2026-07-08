import { SendHorizontal } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/common/Button";

type AIInstructionPanelProps = {
  isSending?: boolean;
  onSend: (instruction: string) => void;
};

export function AIInstructionPanel({ isSending = false, onSend }: AIInstructionPanelProps) {
  const [instruction, setInstruction] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    textarea.style.height = "0px";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
  }, [instruction]);

  function submitInstruction() {
    const trimmedInstruction = instruction.trim();
    if (!trimmedInstruction || isSending) {
      return;
    }

    onSend(trimmedInstruction);
    setInstruction("");
  }

  return (
    <div className="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 px-4 py-3 shadow-[0_-18px_40px_rgba(15,23,42,0.08)] backdrop-blur lg:left-64 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-4xl">
        <div className="rounded-xl border border-slate-200 bg-white p-2 shadow-enterprise">
          <div className="flex items-end gap-2">
            <textarea
              ref={textareaRef}
              value={instruction}
              rows={1}
              placeholder="Ask AI or provide additional instructions..."
              className="max-h-44 min-h-12 flex-1 resize-none rounded-lg border-0 bg-transparent px-3 py-3 text-sm text-slate-900 outline-none placeholder:text-slate-400"
              onChange={(event) => setInstruction(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  submitInstruction();
                }
              }}
            />
            <Button
              type="button"
              className="h-10 w-10 shrink-0 rounded-lg px-0"
              disabled={!instruction.trim() || isSending}
              loading={isSending}
              aria-label="Send instruction"
              onClick={submitInstruction}
            >
              <SendHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <p className="mt-2 text-center text-xs text-slate-500">
          Press Enter to send. Use Shift+Enter for a new line.
        </p>
      </div>
    </div>
  );
}
