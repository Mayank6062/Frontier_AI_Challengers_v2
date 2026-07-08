import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError

from app.prompts.output_prompt import OUTPUT_SYSTEM_PROMPT


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


OUTPUT_FIELDS = {
    "executive_summary",
    "solution_overview",
    "high_level_design",
    "low_level_design",
    "architecture_diagram",
    "data_flow_diagram",
    "security_architecture",
    "deployment_architecture",
    "cost_report",
    "build_vs_buy_report",
    "risk_register",
    "implementation_roadmap",
    "diagrams",
    "downloads",
}


DIAGRAM_FIELDS = {
    "hld",
    "lld",
    "architecture",
    "deployment",
    "data_flow",
    "network",
}


DOWNLOAD_FIELDS = {
    "html",
    "markdown",
    "terraform",
}


class OutputAgentError(RuntimeError):
    pass


class OutputInvalidJSONError(OutputAgentError):
    pass


class OutputAzureError(OutputAgentError):
    pass


class OutputTimeoutError(OutputAgentError):
    pass


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise OutputAgentError(f"Missing required environment variable: {name}")
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
        raise OutputInvalidJSONError(f"Output {field} must be an object")

    missing_fields = expected - set(value)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise OutputInvalidJSONError(f"Output {field} is missing fields: {missing}")


def _parse_output_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise OutputInvalidJSONError("Output generation agent returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise OutputInvalidJSONError("Output generation agent JSON must be an object")

    missing_fields = OUTPUT_FIELDS - set(result)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise OutputInvalidJSONError(f"Output generation JSON is missing fields: {missing}")

    _validate_object_fields(result, "diagrams", DIAGRAM_FIELDS)
    _validate_object_fields(result, "downloads", DOWNLOAD_FIELDS)

    return result


def _build_output_display_data(output: dict[str, Any]) -> dict[str, Any]:
    diagrams = output.get("diagrams", {})

    return {
        "title": "Final Architecture Deliverables",
        "subtitle": "Customer-ready solution package",
        "sections": [
            {
                "heading": "Executive Summary",
                "type": "paragraph",
                "content": output.get("executive_summary", "Not Specified"),
            },
            {
                "heading": "Solution Overview",
                "type": "paragraph",
                "content": output.get("solution_overview", "Not Specified"),
            },
            {
                "heading": "Architecture",
                "type": "mermaid_diagram",
                "diagrams": [
                    {"title": "HLD", "code": diagrams.get("hld", "")},
                    {"title": "LLD", "code": diagrams.get("lld", "")},
                    {"title": "Architecture", "code": diagrams.get("architecture", "")},
                    {"title": "Deployment", "code": diagrams.get("deployment", "")},
                    {"title": "Data Flow", "code": diagrams.get("data_flow", "")},
                    {"title": "Network", "code": diagrams.get("network", "")},
                ],
            },
            {
                "heading": "Roadmap",
                "type": "bullet_list",
                "items": _as_list(output.get("implementation_roadmap")),
            },
            {
                "heading": "Cost",
                "type": "table",
                "rows": _as_list(output.get("cost_report")),
            },
            {
                "heading": "Risk",
                "type": "alert",
                "items": _as_list(output.get("risk_register")),
            },
            {
                "heading": "Downloads",
                "type": "download_card",
                "downloads": [
                    {"label": "Download HTML", "key": "html"},
                    {"label": "Download Markdown", "key": "markdown"},
                    {"label": "Download Terraform", "key": "terraform"},
                ],
            },
        ],
    }


def generate_output(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    if not discovery:
        raise OutputAgentError("Approved discovery output cannot be empty")
    if not knowledge:
        raise OutputAgentError("Approved knowledge output cannot be empty")
    if not recommendation:
        raise OutputAgentError("Approved recommendation output cannot be empty")
    if not architecture:
        raise OutputAgentError("Approved architecture output cannot be empty")
    if not validation:
        raise OutputAgentError("Approved validation output cannot be empty")

    payload = {
        "discovery": discovery,
        "knowledge": knowledge,
        "recommendation": recommendation,
        "architecture": architecture,
        "validation": validation,
    }

    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": OUTPUT_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)},
            ],
            response_format={"type": "json_object"},
        )
    except APITimeoutError as exc:
        raise OutputTimeoutError("Azure OpenAI request timed out") from exc
    except OpenAIError as exc:
        raise OutputAzureError(f"Azure OpenAI request failed: {exc}") from exc
    except Exception as exc:
        raise OutputAgentError(f"Unexpected output generation error: {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise OutputInvalidJSONError("Output generation agent returned an empty response")

    agent_data = _parse_output_json(content)
    downloads = agent_data["downloads"]

    return {
        "agent_data": agent_data,
        "display_data": _build_output_display_data(agent_data),
        "downloads": downloads,
    }
