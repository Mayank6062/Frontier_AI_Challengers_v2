import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError

from app.prompts.architecture_prompt import ARCHITECTURE_SYSTEM_PROMPT


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


ARCHITECTURE_FIELDS = {
    "current_state",
    "target_state",
    "high_level_design",
    "low_level_design",
    "data_flow",
    "deployment_view",
    "integration_view",
    "security_view",
    "network_view",
    "infrastructure_view",
    "architecture_diagram",
    "architecture_summary",
}


ARCHITECTURE_DIAGRAM_FIELDS = {
    "high_level_diagram",
    "data_flow",
    "deployment_view",
    "integration_view",
    "network_view",
    "infrastructure_view",
    "overall_architecture_diagram",
}


class ArchitectureAgentError(RuntimeError):
    pass


class ArchitectureInvalidJSONError(ArchitectureAgentError):
    pass


class ArchitectureAzureError(ArchitectureAgentError):
    pass


class ArchitectureTimeoutError(ArchitectureAgentError):
    pass


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ArchitectureAgentError(f"Missing required environment variable: {name}")
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


def _parse_architecture_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ArchitectureInvalidJSONError("Architecture agent returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise ArchitectureInvalidJSONError("Architecture agent JSON must be an object")

    missing_fields = ARCHITECTURE_FIELDS - set(result)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ArchitectureInvalidJSONError(f"Architecture agent JSON is missing fields: {missing}")

    diagrams = result["architecture_diagram"]
    if not isinstance(diagrams, dict):
        raise ArchitectureInvalidJSONError("Architecture architecture_diagram must be an object")

    missing_diagram_fields = ARCHITECTURE_DIAGRAM_FIELDS - set(diagrams)
    if missing_diagram_fields:
        missing = ", ".join(sorted(missing_diagram_fields))
        raise ArchitectureInvalidJSONError(
            f"Architecture architecture_diagram is missing fields: {missing}"
        )

    return result


def _build_architecture_display_data(architecture: dict[str, Any]) -> dict[str, Any]:
    diagrams = architecture.get("architecture_diagram", {})

    return {
        "title": "Architecture Design Report",
        "subtitle": "Enterprise architecture design for human review",
        "sections": [
            {
                "heading": "Architecture Design",
                "type": "paragraph",
                "content": architecture.get("architecture_summary", "Not Specified"),
            },
            {
                "heading": "Current State",
                "type": "paragraph",
                "content": architecture.get("current_state", "Not Specified"),
            },
            {
                "heading": "Target State",
                "type": "paragraph",
                "content": architecture.get("target_state", "Not Specified"),
            },
            {
                "heading": "High Level Design",
                "type": "bullet_list",
                "items": _as_list(architecture.get("high_level_design")),
            },
            {
                "heading": "Low Level Design",
                "type": "bullet_list",
                "items": _as_list(architecture.get("low_level_design")),
            },
            {
                "heading": "Data Flow",
                "type": "bullet_list",
                "items": _as_list(architecture.get("data_flow")),
            },
            {
                "heading": "Deployment View",
                "type": "bullet_list",
                "items": _as_list(architecture.get("deployment_view")),
            },
            {
                "heading": "Integration View",
                "type": "bullet_list",
                "items": _as_list(architecture.get("integration_view")),
            },
            {
                "heading": "Security View",
                "type": "bullet_list",
                "items": _as_list(architecture.get("security_view")),
            },
            {
                "heading": "Network View",
                "type": "bullet_list",
                "items": _as_list(architecture.get("network_view")),
            },
            {
                "heading": "Infrastructure View",
                "type": "bullet_list",
                "items": _as_list(architecture.get("infrastructure_view")),
            },
            {
                "heading": "Architecture Diagram",
                "type": "mermaid_diagram",
                "diagrams": [
                    {"title": "High Level Diagram", "code": diagrams.get("high_level_diagram", "")},
                    {"title": "Data Flow", "code": diagrams.get("data_flow", "")},
                    {"title": "Deployment View", "code": diagrams.get("deployment_view", "")},
                    {"title": "Integration View", "code": diagrams.get("integration_view", "")},
                    {"title": "Network View", "code": diagrams.get("network_view", "")},
                    {"title": "Infrastructure View", "code": diagrams.get("infrastructure_view", "")},
                    {
                        "title": "Overall Architecture Diagram",
                        "code": diagrams.get("overall_architecture_diagram", ""),
                    },
                ],
            },
            {
                "heading": "Architecture Summary",
                "type": "paragraph",
                "content": architecture.get("architecture_summary", "Not Specified"),
            },
        ],
        "actions": [
            {"label": "Edit Requirement", "action": "edit"},
            {"label": "Approve & Continue", "action": "approve"},
        ],
    }


def generate_architecture(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
) -> dict[str, Any]:
    if not discovery:
        raise ArchitectureAgentError("Approved discovery output cannot be empty")
    if not knowledge:
        raise ArchitectureAgentError("Approved knowledge output cannot be empty")
    if not recommendation:
        raise ArchitectureAgentError("Approved recommendation output cannot be empty")

    payload = {
        "discovery": discovery,
        "knowledge": knowledge,
        "recommendation": recommendation,
    }

    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": ARCHITECTURE_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)},
            ],
            response_format={"type": "json_object"},
        )
    except APITimeoutError as exc:
        raise ArchitectureTimeoutError("Azure OpenAI request timed out") from exc
    except OpenAIError as exc:
        raise ArchitectureAzureError(f"Azure OpenAI request failed: {exc}") from exc
    except Exception as exc:
        raise ArchitectureAgentError(f"Unexpected architecture error: {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise ArchitectureInvalidJSONError("Architecture agent returned an empty response")

    agent_data = _parse_architecture_json(content)

    return {
        "agent_data": agent_data,
        "display_data": _build_architecture_display_data(agent_data),
    }
