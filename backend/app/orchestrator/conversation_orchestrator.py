from __future__ import annotations

from typing import Any

from app.orchestrator.intent_classifier import classify_intent
from app.orchestrator.workflow_state import WorkflowState
from app.orchestrator.workflow_engine import WorkflowEngine


def handle_message(message: str | None, workflow_context: dict[str, Any] | None) -> dict[str, Any]:
    message = (message or "").strip()
    state = WorkflowState(workflow_context)
    state.append_history("user", message)

    intent = classify_intent(message)

    engine = WorkflowEngine(state)

    # Route by intent
    if intent == "START_WORKFLOW":
        result = engine.run_start()
    elif intent == "CONTINUE":
        result = engine.run_continue()
    elif intent == "REQUIREMENT_CHANGE":
        result = engine.run_requirement_change(message)
    elif intent == "CLARIFICATION_ANSWER":
        result = engine.run_clarification_answer(message)
    elif intent == "QUESTION":
        result = engine.run_question(message)
    elif intent == "EXPLAIN":
        result = engine.run_explain(message)
    elif intent == "REGENERATE":
        result = engine.run_regenerate()
    elif intent == "GENERATE_OUTPUT":
        result = engine.run_generate_output()
    elif intent == "STOP":
        result = engine.run_stop()
    else:
        # Unknown: fallback to answering question
        result = engine.run_question(message)

    # Persist assistant message to history if present
    if "assistant_message" in result:
        state.append_history("assistant", result.get("assistant_message"))

    result["workflow_context"] = state.as_dict()
    return result
