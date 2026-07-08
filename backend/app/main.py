from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import JSONResponse

from app.services.llm import ask_llm
from app.orchestrator.conversation_orchestrator import handle_message
from app.services.parser import SUPPORTED_EXTENSIONS, extract_text


app = FastAPI()

# Basic logging for incoming workflow requests
logging.basicConfig(level=logging.INFO)

# Allow frontend dev server to call backend during local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5176", "http://127.0.0.1:5176", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, "", "Not Specified"):
        return []
    return [value]


def _build_discovery_display_data(discovery: dict[str, Any]) -> dict[str, Any]:
    dsa_validation = discovery.get("dsa_validation", {})

    return {
        "title": "Requirement Discovery Report",
        "subtitle": "Professional discovery summary for human review",
        "sections": [
            {
                "heading": "Requirement Intelligence",
                "type": "card",
                "content": discovery.get("requirement_extraction", "Not Specified"),
            },
            {
                "heading": "Requirement Extraction",
                "type": "paragraph",
                "content": discovery.get("requirement_extraction", "Not Specified"),
            },
            {
                "heading": "Functional Requirements",
                "type": "bullet_list",
                "items": _as_list(discovery.get("functional_requirements")),
            },
            {
                "heading": "Non Functional Requirements",
                "type": "bullet_list",
                "items": _as_list(discovery.get("non_functional_requirements")),
            },
            {
                "heading": "Business Goals",
                "type": "bullet_list",
                "items": _as_list(discovery.get("business_goals")),
            },
            {
                "heading": "Constraints",
                "type": "bullet_list",
                "items": _as_list(discovery.get("constraints")),
            },
            {
                "heading": "Assumptions",
                "type": "bullet_list",
                "items": _as_list(discovery.get("assumptions")),
            },
            {
                "heading": "Ambiguity Detection",
                "type": "bullet_list",
                "items": _as_list(discovery.get("ambiguities")),
            },
            {
                "heading": "Clarification Questions",
                "type": "bullet_list",
                "items": _as_list(discovery.get("clarification_questions")),
            },
            {
                "heading": "DSA Validation",
                "type": "metrics",
                "metrics": [
                    {
                        "label": "Requirement Completeness",
                        "value": dsa_validation.get("requirement_completeness", 0),
                        "display": "progress",
                    },
                    {
                        "label": "Business Clarity",
                        "value": dsa_validation.get("business_clarity", 0),
                        "display": "progress",
                    },
                    {
                        "label": "Technical Clarity",
                        "value": dsa_validation.get("technical_clarity", 0),
                        "display": "progress",
                    },
                    {
                        "label": "Risk Level",
                        "value": dsa_validation.get("risk_level", "Not Specified"),
                        "display": "badge",
                    },
                    {
                        "label": "Overall Readiness",
                        "value": dsa_validation.get("overall_readiness", "Not Specified"),
                        "display": "badge",
                    },
                ],
                "missing_critical_information": _as_list(
                    dsa_validation.get("missing_critical_information")
                ),
                "recommendation": dsa_validation.get("recommendation", "Not Specified"),
            },
        ],
        "actions": [
            {"label": "Edit Requirement", "action": "edit"},
            {"label": "Approve & Continue", "action": "approve"},
        ],
    }


def _build_knowledge_display_data(knowledge: dict[str, Any]) -> dict[str, Any]:
    confidence = knowledge.get("knowledge_confidence", {})

    return {
        "title": "Knowledge Enrichment Report",
        "subtitle": "Enterprise knowledge summary for human review",
        "sections": [
            {
                "heading": "Knowledge Retrieval",
                "type": "card",
                "content": knowledge.get("requirement_intelligence", "Not Specified"),
            },
            {
                "heading": "Enterprise Standards",
                "type": "bullet_list",
                "items": _as_list(knowledge.get("enterprise_standards")),
            },
            {
                "heading": "Best Practices",
                "type": "bullet_list",
                "items": _as_list(knowledge.get("best_practices")),
            },
            {
                "heading": "Reference Architectures",
                "type": "bullet_list",
                "items": _as_list(knowledge.get("reference_architectures")),
            },
            {
                "heading": "Technology Catalog",
                "type": "table",
                "rows": knowledge.get("technology_suggestions", {}),
            },
            {
                "heading": "Compliance Standards",
                "type": "bullet_list",
                "items": _as_list(knowledge.get("compliance")),
            },
            {
                "heading": "Previous Approved Solutions",
                "type": "bullet_list",
                "items": [],
            },
            {
                "heading": "Knowledge Confidence",
                "type": "card",
                "level": confidence.get("level", "Not Specified"),
                "content": confidence.get("reason", "Not Specified"),
            },
        ],
        "actions": [
            {"label": "Edit Requirement", "action": "edit"},
            {"label": "Approve & Continue", "action": "approve"},
        ],
    }


def _build_recommendation_display_data(recommendation: dict[str, Any]) -> dict[str, Any]:
    scoring = recommendation.get("architecture_scoring", {})

    return {
        "title": "Recommendation Report",
        "subtitle": "Enterprise architecture recommendations for human review",
        "sections": [
            {
                "heading": "Architecture Pattern Recommendation",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("architecture_pattern_recommendation")),
            },
            {
                "heading": "Technology Recommendation",
                "type": "table",
                "rows": recommendation.get("technology_recommendation", {}),
            },
            {
                "heading": "Cloud Recommendation",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("cloud_recommendation")),
            },
            {
                "heading": "Build vs Buy",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("build_vs_buy_analysis")),
            },
            {
                "heading": "Data Flow Recommendation",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("data_flow_recommendation")),
            },
            {
                "heading": "Integration Recommendation",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("integration_recommendation")),
            },
            {
                "heading": "Security Recommendation",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("security_recommendation")),
            },
            {
                "heading": "Architecture Simplification",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("architecture_simplification")),
            },
            {
                "heading": "Cost Recommendation",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("cost_recommendation")),
            },
            {
                "heading": "Risk Recommendation",
                "type": "alert",
                "items": _as_list(recommendation.get("risk_recommendation")),
            },
            {
                "heading": "Architecture Candidates",
                "type": "bullet_list",
                "items": _as_list(recommendation.get("architecture_candidate_generation")),
            },
            {
                "heading": "Architecture Score",
                "type": "score_card",
                "recommended_candidate": scoring.get("recommended_candidate", "Not Specified"),
                "scores": _as_list(scoring.get("scores")),
            },
        ],
        "actions": [
            {"label": "Edit Requirement", "action": "edit"},
            {"label": "Approve & Continue", "action": "approve"},
        ],
    }


def _workflow_context_from_request(request_body: dict[str, Any]) -> dict[str, Any]:
    workflow_ctx = request_body.get("workflow_context")
    if isinstance(workflow_ctx, dict):
        return dict(workflow_ctx)

    # Legacy clients may send agent_data, but execution still goes through the orchestrator.
    agent_data = request_body.get("agent_data")
    if isinstance(agent_data, dict) and "current_stage" in agent_data:
        return dict(agent_data)

    return {}


def _message_from_request(request_body: dict[str, Any], workflow_ctx: dict[str, Any]) -> str:
    action = str(request_body.get("action") or "").lower().strip()

    if action == "start" and request_body.get("requirement"):
        workflow_ctx["requirement"] = request_body["requirement"]
        return "start workflow"

    if action == "approve":
        return "continue"

    return str(
        request_body.get("message")
        or request_body.get("instruction")
        or request_body.get("requirement")
        or ""
    )


def _log_workflow_request_state(workflow_ctx: dict[str, Any]) -> None:
    logging.info(
        "/workflow state: current_stage=%s completed_stages=%s workflow_context_keys=%s",
        workflow_ctx.get("current_stage"),
        workflow_ctx.get("completed_stages"),
        sorted(workflow_ctx.keys()),
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "running"}


@app.get("/test-llm")
def test_llm() -> dict[str, str]:
    try:
        response = ask_llm("Say Hello from Azure OpenAI")
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"response": response}


@app.post("/upload", response_model=None)
def upload_requirement(file: UploadFile | None = File(None)) -> dict[str, str] | JSONResponse:
    if file is None:
        return JSONResponse(status_code=400, content={"error": "Missing file"})

    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "Missing file"})

    extension = Path(file.filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        return JSONResponse(status_code=400, content={"error": "Unsupported file type"})

    try:
        text = extract_text(file)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    if not text.strip():
        return JSONResponse(status_code=400, content={"error": "Extracted text is empty"})

    return {
        "filename": file.filename,
        "file_type": extension.lstrip("."),
        "text": text,
    }


@app.post("/workflow")
def workflow(request_body: dict | None = Body(None)) -> dict[str, Any]:
    if request_body is None:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    logging.info("/workflow called with body: %s", request_body)
    workflow_ctx = _workflow_context_from_request(request_body)
    message = _message_from_request(request_body, workflow_ctx)
    _log_workflow_request_state(workflow_ctx)

    try:
        return handle_message(message, workflow_ctx)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {exc}") from exc


@app.post("/workflow/")
def workflow_slash(request_body: dict | None = Body(None)) -> dict[str, Any]:
    # Accept requests with a trailing slash — delegate to primary handler
    return workflow(request_body)
