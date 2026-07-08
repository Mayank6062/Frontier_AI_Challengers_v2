import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError

from app.prompts.discovery_prompt import DISCOVERY_SYSTEM_PROMPT


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


DISCOVERY_FIELDS = {
    "requirement_extraction",
    "functional_requirements",
    "non_functional_requirements",
    "business_goals",
    "constraints",
    "assumptions",
    "ambiguities",
    "clarification_questions",
    "dsa_validation",
}


DSA_VALIDATION_FIELDS = {
    "requirement_completeness",
    "business_clarity",
    "technical_clarity",
    "risk_level",
    "overall_readiness",
    "missing_critical_information",
    "recommendation",
}


class DiscoveryAgentError(RuntimeError):
    pass


class DiscoveryInvalidJSONError(DiscoveryAgentError):
    pass


class DiscoveryAzureError(DiscoveryAgentError):
    pass


class DiscoveryTimeoutError(DiscoveryAgentError):
    pass


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise DiscoveryAgentError(f"Missing required environment variable: {name}")
    return value


def _create_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=_get_required_env("AZURE_OPENAI_API_KEY"),
        azure_endpoint=_get_required_env("AZURE_OPENAI_ENDPOINT"),
        api_version=_get_required_env("AZURE_OPENAI_API_VERSION"),
        timeout=60.0,
    )


def _parse_discovery_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise DiscoveryInvalidJSONError("Discovery agent returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise DiscoveryInvalidJSONError("Discovery agent JSON must be an object")

    missing_fields = DISCOVERY_FIELDS - set(result)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise DiscoveryInvalidJSONError(f"Discovery agent JSON is missing fields: {missing}")

    dsa_validation = result["dsa_validation"]
    if not isinstance(dsa_validation, dict):
        raise DiscoveryInvalidJSONError("Discovery agent dsa_validation must be an object")

    missing_dsa_fields = DSA_VALIDATION_FIELDS - set(dsa_validation)
    if missing_dsa_fields:
        missing = ", ".join(sorted(missing_dsa_fields))
        raise DiscoveryInvalidJSONError(f"Discovery agent dsa_validation is missing fields: {missing}")

    return result


def discover_requirement(requirement_text: str) -> dict[str, Any]:
    if not requirement_text.strip():
        raise DiscoveryAgentError("Requirement text cannot be empty")

    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": DISCOVERY_SYSTEM_PROMPT},
                {"role": "user", "content": requirement_text},
            ],
            response_format={"type": "json_object"},
        )
    except APITimeoutError as exc:
        raise DiscoveryTimeoutError("Azure OpenAI request timed out") from exc
    except OpenAIError as exc:
        raise DiscoveryAzureError(f"Azure OpenAI request failed: {exc}") from exc
    except Exception as exc:
        raise DiscoveryAgentError(f"Unexpected discovery error: {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise DiscoveryInvalidJSONError("Discovery agent returned an empty response")

    return _parse_discovery_json(content)
