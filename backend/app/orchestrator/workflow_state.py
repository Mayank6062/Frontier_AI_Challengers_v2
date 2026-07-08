from __future__ import annotations

from typing import Any


STAGE_ORDER = ["discovery", "knowledge", "recommendation", "architecture", "validation", "output"]


DEFAULT_WORKFLOW = {
    "requirement": "",
    "discovery": None,
    "knowledge": None,
    "recommendation": None,
    "architecture": None,
    "validation": None,
    "output": None,
    "current_stage": None,
    "generated_stages": [],
    "approved_stages": [],
    "completed_stages": [],
    "conversation_history": [],
    "pending_questions": [],
}


class WorkflowState:
    def __init__(self, ctx: dict[str, Any] | None = None) -> None:
        data = ctx or {}
        merged = {**DEFAULT_WORKFLOW, **data}
        # Keep legacy completed_stages readable, but drive workflow semantics from approval state.
        if not merged.get("approved_stages") and merged.get("completed_stages"):
            merged["approved_stages"] = list(merged.get("completed_stages") or [])

        generated = list(merged.get("generated_stages") or [])
        for stage in STAGE_ORDER:
            if stage in merged and merged.get(stage) is not None and stage not in generated:
                generated.append(stage)

        merged["generated_stages"] = generated
        merged["approved_stages"] = list(merged.get("approved_stages") or [])
        merged["completed_stages"] = list(merged.get("completed_stages") or [])
        merged["conversation_history"] = list(merged.get("conversation_history") or [])
        merged["pending_questions"] = list(merged.get("pending_questions") or [])
        self._state = merged

    def as_dict(self) -> dict[str, Any]:
        self._state["completed_stages"] = list(self._state.get("approved_stages") or [])
        return dict(self._state)

    # Basic accessors
    def get(self, key: str, default=None):
        return self._state.get(key, default)

    def set(self, key: str, value) -> None:
        self._state[key] = value

    def append_history(self, role: str, message: str) -> None:
        self._state["conversation_history"].append({"role": role, "message": message})

    def mark_stage_generated(self, stage: str) -> None:
        if stage and stage not in self._state["generated_stages"]:
            self._state["generated_stages"].append(stage)

    def mark_stage_approved(self, stage: str) -> None:
        if stage and stage not in self._state["approved_stages"]:
            self._state["approved_stages"].append(stage)
        self._state["completed_stages"] = list(self._state["approved_stages"])

    def mark_stage_completed(self, stage: str) -> None:
        self.mark_stage_approved(stage)

    def reset_from_stage(self, stage: str) -> None:
        if stage not in STAGE_ORDER:
            return
        idx = STAGE_ORDER.index(stage)
        for s in STAGE_ORDER[idx:]:
            self._state[s] = None
            if s in self._state["generated_stages"]:
                self._state["generated_stages"].remove(s)
            if s in self._state["approved_stages"]:
                self._state["approved_stages"].remove(s)
            if s in self._state["completed_stages"]:
                self._state["completed_stages"].remove(s)
        self._state["current_stage"] = None
        self._state["pending_questions"] = []
