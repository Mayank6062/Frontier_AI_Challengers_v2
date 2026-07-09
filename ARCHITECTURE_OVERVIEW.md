# Architecture Overview

An AI-assisted software-architecture generator: a user uploads a requirement document, and a chain of LLM "agents" progressively turns it into a discovery report → enriched knowledge → recommendations → architecture design → validation → a final output document, with human approval gating each stage.

## Backend (`backend/app`, FastAPI + Azure OpenAI)

### Entry point — `main.py`
- `POST /upload`: accepts a file, extracts its text via `services/parser.py`.
- `POST /workflow` (and `/workflow/`): the single endpoint the frontend talks to for everything else. It normalizes the incoming request into a `workflow_ctx` dict + a `message` string, then hands off to `handle_message`.
- A large chunk of `main.py` is `_build_*_display_data` functions — pure formatters that turn each agent's raw JSON into a generic `{title, sections[], actions[]}` shape the frontend renders without stage-specific UI code.

### Orchestrator — the real brain
- `orchestrator/conversation_orchestrator.py`: `handle_message()` loads a `WorkflowState`, classifies the user's message into an intent, and dispatches to the matching `WorkflowEngine` method.
- `orchestrator/intent_classifier.py`: a keyword-based (not LLM-based) classifier mapping free text to intents like `START_WORKFLOW`, `CONTINUE`, `REQUIREMENT_CHANGE`, `CLARIFICATION_ANSWER`, `QUESTION`, `REGENERATE`, `GENERATE_OUTPUT`, `STOP`.
- `orchestrator/workflow_state.py`: a plain-dict-backed state object tracking the 6-stage pipeline (`discovery → knowledge → recommendation → architecture → validation → output`), which stages are generated vs. approved, and conversation history. Since the backend is stateless between requests, the frontend round-trips the entire `workflow_context` on every call and the server treats it as source of truth.
- `orchestrator/workflow_engine.py`: the core state machine.
  - `run_start`/`run_continue`/`run_regenerate` drive stage generation in order, checking each stage's prerequisite data exists (`_missing_stage_data_response` if not) before calling its agent function.
  - `run_continue` only advances once the *current* stage is approved (`_approve_current_stage`), enforcing the human-in-the-loop review gate.
  - `run_requirement_change`/`run_clarification_answer` use an LLM call (`_merge_requirement`) to merge new user input into the existing requirement text, then reset the pipeline from `discovery` onward.
  - `run_question`/`run_explain` are side-channel LLM Q&A over the current context without mutating workflow state.

### Agents — one per stage (`backend/app/agents/*.py`)
Each agent is basically: build a system prompt (from `backend/app/prompts/*.py`) → call Azure OpenAI with `response_format=json_object` → strictly validate the returned JSON has all expected fields (raising typed errors like `DiscoveryInvalidJSONError` otherwise) → return the parsed dict.

### LLM service — `services/llm.py`
Thin wrapper (`ask_llm`) around `AzureOpenAI` client creation + a single chat completion call, used for the free-form (non-agent) LLM calls like question-answering and requirement merging.

## Frontend (`frontend/src`, React + Vite + TS)

- `App.tsx`: wraps everything in `WorkflowProvider` and defines routes — Upload, Workspace, History, Settings.
- `hooks/useWorkflow.tsx`: a context/hook holding all workflow client state (`currentStage`, `displayData`, `workflowContext`). `uploadAndStart` and `sendInstruction` both call `sendWorkflowInstruction` (`services/workflow.ts`) and feed the response into `applyWorkflowResponse`, which trusts the backend's `workflow_context` and `display_data` as-is (generic renderer, no per-stage UI logic on the client).
- Components under `components/workflow/` (`AIInstructionPanel`, `OutputWorkspace`, `WorkflowTimeline`) render that generic `display_data` and let the user type free-text instructions, which map straight to `intent_classifier.py` on the backend.

## Key design pattern worth noting

The whole system hinges on a **generic display schema** (`sections` with `type: card|bullet_list|table|metrics|score_card|alert`) — agents/backend decide *what* to show, frontend only knows *how* to render each block type. That's why adding a new stage or field mostly means backend changes only.
