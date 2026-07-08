import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError

from app.prompts.validation_prompt import VALIDATION_SYSTEM_PROMPT


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


VALIDATION_FIELDS = {
    "architecture_review",
    "best_practice_validation",
    "compliance_validation",
    "security_validation",
    "cost_validation",
    "performance_validation",
    "scalability_validation",
    "reliability_validation",
    "observability_validation",
    "risk_validation",
    "architecture_score",
    "final_recommendation",
}


SECURITY_FIELDS = {
    "authentication",
    "authorization",
    "encryption",
    "secrets",
    "iam",
    "network_security",
    "api_security",
}


COST_FIELDS = {
    "estimated_cost",
    "optimization_opportunities",
    "resource_utilization",
}


PERFORMANCE_FIELDS = {
    "latency",
    "throughput",
    "caching",
    "database_performance",
}


SCALABILITY_FIELDS = {
    "horizontal_scaling",
    "vertical_scaling",
    "auto_scaling",
    "elasticity",
}


RELIABILITY_FIELDS = {
    "high_availability",
    "disaster_recovery",
    "backup_strategy",
    "fault_tolerance",
}


OBSERVABILITY_FIELDS = {
    "logging",
    "monitoring",
    "tracing",
    "alerting",
    "dashboards",
}


RISK_FIELDS = {
    "high_risks",
    "medium_risks",
    "low_risks",
    "mitigation_suggestions",
}


SCORE_FIELDS = {
    "overall_score",
    "security",
    "performance",
    "scalability",
    "maintainability",
    "reliability",
    "cost",
    "compliance",
}


FINAL_RECOMMENDATIONS = {
    "Approved",
    "Approved With Recommendations",
    "Needs Improvement",
    "Rejected",
}


class ValidationAgentError(RuntimeError):
    pass


class ValidationInvalidJSONError(ValidationAgentError):
    pass


class ValidationAzureError(ValidationAgentError):
    pass


class ValidationTimeoutError(ValidationAgentError):
    pass


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValidationAgentError(f"Missing required environment variable: {name}")
    return value


def _create_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=_get_required_env("AZURE_OPENAI_API_KEY"),
        azure_endpoint=_get_required_env("AZURE_OPENAI_ENDPOINT"),
        api_version=_get_required_env("AZURE_OPENAI_API_VERSION"),
        timeout=60.0,
    )


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, "", "Not Specified"):
        return []
    return [value]


def _validate_object_fields(result: dict[str, Any], field: str, expected: set[str]) -> None:
    value = result[field]
    if not isinstance(value, dict):
        raise ValidationInvalidJSONError(f"Validation {field} must be an object")

    missing_fields = expected - set(value)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValidationInvalidJSONError(f"Validation {field} is missing fields: {missing}")


def _parse_validation_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValidationInvalidJSONError("Validation agent returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise ValidationInvalidJSONError("Validation agent JSON must be an object")

    missing_fields = VALIDATION_FIELDS - set(result)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValidationInvalidJSONError(f"Validation agent JSON is missing fields: {missing}")

    nested_fields = {
        "security_validation": SECURITY_FIELDS,
        "cost_validation": COST_FIELDS,
        "performance_validation": PERFORMANCE_FIELDS,
        "scalability_validation": SCALABILITY_FIELDS,
        "reliability_validation": RELIABILITY_FIELDS,
        "observability_validation": OBSERVABILITY_FIELDS,
        "risk_validation": RISK_FIELDS,
        "architecture_score": SCORE_FIELDS,
    }

    for field, expected in nested_fields.items():
        _validate_object_fields(result, field, expected)

    if result["final_recommendation"] not in FINAL_RECOMMENDATIONS:
        raise ValidationInvalidJSONError("Validation final_recommendation has an invalid value")

    return result


def _build_validation_display_data(validation: dict[str, Any]) -> dict[str, Any]:
    scores = validation.get("architecture_score", {})
    risks = validation.get("risk_validation", {})

    return {
        "title": "Architecture Validation Report",
        "subtitle": "Architecture Review Board validation summary",
        "sections": [
            {
                "heading": "Architecture Review",
                "type": "paragraph",
                "content": validation.get("architecture_review", "Not Specified"),
            },
            {
                "heading": "Best Practice Validation",
                "type": "bullet_list",
                "items": _as_list(validation.get("best_practice_validation")),
            },
            {
                "heading": "Compliance Validation",
                "type": "bullet_list",
                "items": _as_list(validation.get("compliance_validation")),
            },
            {
                "heading": "Security Validation",
                "type": "table",
                "rows": validation.get("security_validation", {}),
            },
            {
                "heading": "Cost Validation",
                "type": "table",
                "rows": validation.get("cost_validation", {}),
            },
            {
                "heading": "Performance Validation",
                "type": "table",
                "rows": validation.get("performance_validation", {}),
            },
            {
                "heading": "Scalability Validation",
                "type": "table",
                "rows": validation.get("scalability_validation", {}),
            },
            {
                "heading": "Reliability Validation",
                "type": "table",
                "rows": validation.get("reliability_validation", {}),
            },
            {
                "heading": "Observability Validation",
                "type": "table",
                "rows": validation.get("observability_validation", {}),
            },
            {
                "heading": "Risk Validation",
                "type": "alert",
                "risks": {
                    "high": _as_list(risks.get("high_risks")),
                    "medium": _as_list(risks.get("medium_risks")),
                    "low": _as_list(risks.get("low_risks")),
                    "mitigation_suggestions": _as_list(risks.get("mitigation_suggestions")),
                },
            },
            {
                "heading": "Architecture Score",
                "type": "score_card",
                "scores": [
                    {"label": "Overall Score", "value": scores.get("overall_score", 0), "display": "progress_bar"},
                    {"label": "Security", "value": scores.get("security", 0), "display": "progress_bar"},
                    {"label": "Performance", "value": scores.get("performance", 0), "display": "progress_bar"},
                    {"label": "Scalability", "value": scores.get("scalability", 0), "display": "progress_bar"},
                    {"label": "Maintainability", "value": scores.get("maintainability", 0), "display": "progress_bar"},
                    {"label": "Reliability", "value": scores.get("reliability", 0), "display": "progress_bar"},
                    {"label": "Cost", "value": scores.get("cost", 0), "display": "progress_bar"},
                    {"label": "Compliance", "value": scores.get("compliance", 0), "display": "progress_bar"},
                ],
            },
            {
                "heading": "Final Recommendation",
                "type": "alert",
                "content": validation.get("final_recommendation", "Not Specified"),
            },
        ],
        "actions": [
            {"label": "Edit Requirement", "action": "edit"},
            {"label": "Approve & Continue", "action": "approve"},
        ],
    }


def generate_validation(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
) -> dict[str, Any]:
    if not discovery:
        raise ValidationAgentError("Approved discovery output cannot be empty")
    if not knowledge:
        raise ValidationAgentError("Approved knowledge output cannot be empty")
    if not recommendation:
        raise ValidationAgentError("Approved recommendation output cannot be empty")
    if not architecture:
        raise ValidationAgentError("Approved architecture output cannot be empty")

    payload = {
        "discovery": discovery,
        "knowledge": knowledge,
        "recommendation": recommendation,
        "architecture": architecture,
    }

    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": VALIDATION_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)},
            ],
            response_format={"type": "json_object"},
        )
    except APITimeoutError as exc:
        raise ValidationTimeoutError("Azure OpenAI request timed out") from exc
    except OpenAIError as exc:
        raise ValidationAzureError(f"Azure OpenAI request failed: {exc}") from exc
    except Exception as exc:
        raise ValidationAgentError(f"Unexpected validation error: {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise ValidationInvalidJSONError("Validation agent returned an empty response")

    agent_data = _parse_validation_json(content)

    return {
        "agent_data": agent_data,
        "display_data": _build_validation_display_data(agent_data),
    }
