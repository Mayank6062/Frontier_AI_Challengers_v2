from __future__ import annotations
 
import json
import logging
from typing import Any
 
from app.orchestrator.workflow_state import WorkflowState
from app.services.llm import ask_llm
from app.agents.discovery_agent import discover_requirement
from app.agents.knowledge_agent import generate_knowledge
from app.agents.recommendation_agent import generate_recommendation
from app.agents.architecture_agent import (
    _build_architecture_display_data,
    generate_architecture,
)
from app.agents.validation_agent import (
    _build_validation_display_data,
    generate_validation,
)
from app.agents.output_agent import _build_output_display_data, generate_output
 
 
STAGE_ORDER = ["discovery", "knowledge", "recommendation", "architecture", "validation", "output"]
logger = logging.getLogger(__name__)
 
 
class WorkflowEngine:
    def __init__(self, state: WorkflowState) -> None:
        self.state = state
 
    def _approved_stages(self) -> list[str]:
        return list(self.state.get("approved_stages") or [])
 
    def _generated_stages(self) -> list[str]:
        return list(self.state.get("generated_stages") or [])
 
    def _next_unapproved_stage(self) -> str | None:
        approved = self._approved_stages()
        for stage in STAGE_ORDER:
            if stage not in approved:
                return stage
        return None
 
    def _stage_after(self, stage: str) -> str | None:
        if stage not in STAGE_ORDER:
            return None
        idx = STAGE_ORDER.index(stage) + 1
        return STAGE_ORDER[idx] if idx < len(STAGE_ORDER) else None
 
    def _current_agent_data(self) -> Any:
        current = self.state.get("current_stage")
        if current in STAGE_ORDER:
            return self.state.get(current) or {}
        return {}
 
    def _empty_display(self, title: str = "Workflow Context") -> dict[str, Any]:
        return {
            "title": title,
            "subtitle": "No document is currently available for review.",
            "sections": [],
            "actions": [],
        }
 
    def _error_display(
        self,
        title: str,
        message: str,
        subtitle: str = "The workflow could not continue.",
    ) -> dict[str, Any]:
        return {
            "title": title,
            "subtitle": subtitle,
            "sections": [
                {
                    "heading": "Workflow Error",
                    "type": "alert",
                    "content": message,
                }
            ],
            "actions": [],
        }
 
    def _stage_display_data(self, stage: str | None, agent_data: Any) -> dict[str, Any]:
        if not stage or not isinstance(agent_data, dict) or not agent_data:
            return self._empty_display()
 
        if stage == "architecture" and "agent_data" in agent_data:
            agent_data = agent_data.get("agent_data") or {}
        if stage == "validation" and "agent_data" in agent_data:
            agent_data = agent_data.get("agent_data") or {}
        if stage == "output" and "agent_data" in agent_data:
            agent_data = agent_data.get("agent_data") or {}
 
        if stage == "discovery":
            from app.main import _build_discovery_display_data
 
            return _build_discovery_display_data(agent_data)
        if stage == "knowledge":
            from app.main import _build_knowledge_display_data
 
            return _build_knowledge_display_data(agent_data)
        if stage == "recommendation":
            from app.main import _build_recommendation_display_data
 
            return _build_recommendation_display_data(agent_data)
        if stage == "architecture":
            return _build_architecture_display_data(agent_data)
        if stage == "validation":
            return _build_validation_display_data(agent_data)
        if stage == "output":
            return _build_output_display_data(agent_data)
 
        return self._empty_display()
 
    def _response(
        self,
        *,
        status: str,
        display_data: dict[str, Any] | None = None,
        agent_data: Any | None = None,
        assistant_message: str = "",
        next_expected_action: str | list[str] = "",
    ) -> dict[str, Any]:
        current = self.state.get("current_stage")
        if agent_data is None:
            agent_data = self._current_agent_data()
        if display_data is None:
            display_data = self._stage_display_data(current, agent_data)
 
        return {
            "status": status,
            "workflow_context": self.state.as_dict(),
            "display_data": display_data or self._empty_display(),
            "agent_data": agent_data or {},
            "assistant_message": assistant_message,
            "next_expected_action": next_expected_action,
        }
 
    def _missing_stage_data_response(self, stage: str, missing: list[str]) -> dict[str, Any]:
        missing_text = ", ".join(missing)
        message = f"Cannot generate {stage}: missing required workflow data: {missing_text}."
        return self._response(
            status="workflow_context_error",
            display_data=self._error_display(
                "Missing Workflow Context",
                message,
                subtitle="The workflow could not continue because required context is missing.",
            ),
            agent_data={
                "error": "missing_required_stage_data",
                "stage": stage,
                "missing": missing,
            },
            assistant_message=message,
            next_expected_action="retry_or_restart_workflow",
        )
 
    def _normalize_agent_result(self, result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
        if isinstance(result, dict) and "agent_data" in result:
            return result.get("agent_data") or {}, result.get("display_data")
        return result, None
 
    def _stage_generation_error_response(self, stage: str, exc: Exception) -> dict[str, Any]:
        title = f"{stage.replace('_', ' ').title()} Generation Failed"
        message = f"{stage.replace('_', ' ').title()} could not be generated: {exc}"
        return self._response(
            status=f"{stage}_generation_error",
            display_data=self._error_display(title, message),
            agent_data={
                "error": f"{stage}_generation_failed",
                "message": str(exc),
            },
            assistant_message=message,
            next_expected_action="retry_or_request_changes",
        )
 
    def _generate_stage(self, stage: str) -> dict[str, Any]:
        if stage == "discovery":
            try:
                result = discover_requirement(self.state.get("requirement") or "")
                agent_data, display_data = result, self._stage_display_data(stage, result)
            except Exception as exc:
                logger.exception("Discovery generation failed")
                return self._stage_generation_error_response("discovery", exc)
        elif stage == "knowledge":
            discovery = self.state.get("discovery")
            if discovery is None:
                return self._missing_stage_data_response("knowledge", ["discovery"])
            try:
                result = generate_knowledge(discovery)
                agent_data, display_data = result, self._stage_display_data(stage, result)
            except Exception as exc:
                logger.exception("Knowledge generation failed")
                return self._stage_generation_error_response("knowledge", exc)
        elif stage == "recommendation":
            discovery = self.state.get("discovery")
            knowledge = self.state.get("knowledge")
            logger.info(
                (
                    "Before Recommendation Agent: current_stage=%s completed_stages=%s "
                    "workflow_context_keys=%s discovery exists? %s; knowledge exists? %s"
                ),
                self.state.get("current_stage"),
                self.state.get("completed_stages"),
                sorted(self.state.as_dict().keys()),
                discovery is not None,
                knowledge is not None,
            )
            missing = []
            if discovery is None:
                missing.append("discovery")
            if knowledge is None:
                missing.append("knowledge")
            if missing:
                return self._missing_stage_data_response("recommendation", missing)
            try:
                result = generate_recommendation(discovery, knowledge)
                agent_data, display_data = result, self._stage_display_data(stage, result)
            except Exception as exc:
                logger.exception("After Recommendation Agent: response generated successfully? False")
                return self._stage_generation_error_response("recommendation", exc)
            logger.info("After Recommendation Agent: response generated successfully? %s", True)
        elif stage == "architecture":
            missing = [
                required
                for required in ("discovery", "knowledge", "recommendation")
                if self.state.get(required) is None
            ]
            if missing:
                return self._missing_stage_data_response("architecture", missing)
            try:
                result = generate_architecture(
                    self.state.get("discovery"),
                    self.state.get("knowledge"),
                    self.state.get("recommendation"),
                )
                agent_data, display_data = self._normalize_agent_result(result)
            except Exception as exc:
                logger.exception("Architecture generation failed")
                return self._stage_generation_error_response("architecture", exc)
        elif stage == "validation":
            missing = [
                required
                for required in ("discovery", "knowledge", "recommendation", "architecture")
                if self.state.get(required) is None
            ]
            if missing:
                return self._missing_stage_data_response("validation", missing)
            try:
                result = generate_validation(
                    self.state.get("discovery"),
                    self.state.get("knowledge"),
                    self.state.get("recommendation"),
                    self.state.get("architecture"),
                )
                agent_data, display_data = self._normalize_agent_result(result)
            except Exception as exc:
                logger.exception("Validation generation failed")
                return self._stage_generation_error_response("validation", exc)
        elif stage == "output":
            missing = [
                required
                for required in (
                    "discovery",
                    "knowledge",
                    "recommendation",
                    "architecture",
                    "validation",
                )
                if self.state.get(required) is None
            ]
            if missing:
                return self._missing_stage_data_response("output", missing)
            try:
                result = generate_output(
                    self.state.get("discovery"),
                    self.state.get("knowledge"),
                    self.state.get("recommendation"),
                    self.state.get("architecture"),
                    self.state.get("validation"),
                )
                agent_data, display_data = self._normalize_agent_result(result)
            except Exception as exc:
                logger.exception("Output generation failed")
                return self._stage_generation_error_response("output", exc)
        else:
            return self._response(
                status="unsupported",
                agent_data={},
                display_data=self._empty_display("Unsupported Workflow Stage"),
                assistant_message=f"Unsupported workflow stage: {stage}",
                next_expected_action="review_current_stage",
            )
 
        self.state.set(stage, agent_data)
        self.state.set("current_stage", stage)
        self.state.mark_stage_generated(stage)
 
        if stage == "discovery":
            self.state.set("pending_questions", agent_data.get("clarification_questions") or [])
 
        return self._response(
            status="waiting_for_review",
            display_data=display_data or self._stage_display_data(stage, agent_data),
            agent_data=agent_data,
            assistant_message=f"{stage.replace('_', ' ').title()} is ready for review.",
            next_expected_action="continue_or_request_changes",
        )
 
    def _approve_current_stage(self) -> str | None:
        current = self.state.get("current_stage")
        if current in STAGE_ORDER and current in self._generated_stages():
            self.state.mark_stage_approved(current)
            if current == "discovery":
                self.state.set("pending_questions", [])
            return current
        return None
 
    def _merge_requirement(self, message: str, change_type: str) -> str:
        existing = self.state.get("requirement") or ""
        prompt = f"""
You are updating a software architecture requirement.
 
Return only valid JSON with this shape:
{{"requirement": "the fully merged requirement"}}
 
Rules:
- Preserve existing requirement details unless the new message explicitly changes them.
- Integrate the new information into the right place in the requirement.
- Do not append a raw transcript or label.
- Resolve clarification answers into the requirement context.
 
Existing requirement:
{existing}
 
New {change_type}:
{message}
""".strip()
 
        try:
            response = ask_llm(prompt)
            parsed = json.loads(response)
            merged = parsed.get("requirement") if isinstance(parsed, dict) else None
            if isinstance(merged, str) and merged.strip():
                return merged.strip()
        except Exception:
            pass
 
        if not existing:
            return message.strip()
        return f"{existing.strip()}\n\nUpdated requirement context: {message.strip()}"
 
    def run_start(self) -> dict[str, Any]:
        if not self.state.get("requirement"):
            history = self.state.get("conversation_history") or []
            for item in reversed(history):
                if item.get("role") == "user" and item.get("message"):
                    self.state.set("requirement", item["message"])
                    break
 
        self.state.reset_from_stage("discovery")
        return self._generate_stage("discovery")
 
    def run_continue(self) -> dict[str, Any]:
        approved = self._approve_current_stage()
        if approved:
            next_stage = self._stage_after(approved)
        else:
            next_stage = self._next_unapproved_stage()
 
        if not next_stage:
            return self._response(
                status="complete",
                display_data=self._stage_display_data(self.state.get("current_stage"), self._current_agent_data()),
                assistant_message="Workflow is complete.",
                next_expected_action="workflow_complete",
            )
 
        return self._generate_stage(next_stage)
 
    def run_requirement_change(self, message: str) -> dict[str, Any]:
        self.state.set("requirement", self._merge_requirement(message, "requirement change"))
        self.state.reset_from_stage("discovery")
        return self._generate_stage("discovery")
 
    def run_clarification_answer(self, message: str) -> dict[str, Any]:
        self.state.set("requirement", self._merge_requirement(message, "clarification answer"))
        self.state.reset_from_stage("discovery")
        return self._generate_stage("discovery")
 
    def run_question(self, message: str) -> dict[str, Any]:
        prompt = (
            "Answer the following question using this workflow context.\n\n"
            f"Context: {self.state.as_dict()}\n\nQuestion: {message}"
        )
        answer = ask_llm(prompt)
        return self._response(
            status="answered",
            assistant_message=answer,
            next_expected_action="continue_or_ask_question",
        )
 
    def run_explain(self, message: str) -> dict[str, Any]:
        prompt = (
            "Explain the current workflow report to a human reviewer.\n\n"
            f"Context: {self.state.as_dict()}\n\nUser request: {message}"
        )
        answer = ask_llm(prompt)
        return self._response(
            status="explained",
            assistant_message=answer,
            next_expected_action="continue_or_ask_question",
        )
 
    def run_regenerate(self) -> dict[str, Any]:
        current = self.state.get("current_stage")
        if current not in STAGE_ORDER:
            return self._response(
                status="no_current_stage",
                display_data=self._empty_display("No Current Stage"),
                agent_data={},
                assistant_message="There is no current workflow stage to regenerate.",
                next_expected_action="start_workflow",
            )
 
        self.state.reset_from_stage(current)
        return self._generate_stage(current)
 
    def run_generate_output(self) -> dict[str, Any]:
        current = self.state.get("current_stage")
        if current in STAGE_ORDER and current in self._generated_stages():
            self.state.mark_stage_approved(current)
        return self._generate_stage("output")
 
    def run_stop(self) -> dict[str, Any]:
        return self._response(
            status="stopped",
            assistant_message="Workflow stopped by user.",
            next_expected_action="start_or_continue",
        )
 