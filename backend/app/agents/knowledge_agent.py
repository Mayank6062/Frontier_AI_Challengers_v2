import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError

from app.prompts.knowledge_prompt import KNOWLEDGE_SYSTEM_PROMPT


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


KNOWLEDGE_FIELDS = {
    "requirement_intelligence",
    "enterprise_standards",
    "best_practices",
    "architecture_patterns",
    "technology_suggestions",
    "compliance",
    "reference_architectures",
    "knowledge_confidence",
}


KNOWLEDGE_CONFIDENCE_FIELDS = {
    "level",
    "reason",
}


class KnowledgeAgentError(RuntimeError):
    pass


class KnowledgeInvalidJSONError(KnowledgeAgentError):
    pass


class KnowledgeAzureError(KnowledgeAgentError):
    pass


class KnowledgeTimeoutError(KnowledgeAgentError):
    pass


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise KnowledgeAgentError(f"Missing required environment variable: {name}")
    return value


def _create_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=_get_required_env("AZURE_OPENAI_API_KEY"),
        azure_endpoint=_get_required_env("AZURE_OPENAI_ENDPOINT"),
        api_version=_get_required_env("AZURE_OPENAI_API_VERSION"),
        timeout=60.0,
    )


def _parse_knowledge_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise KnowledgeInvalidJSONError("Knowledge agent returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise KnowledgeInvalidJSONError("Knowledge agent JSON must be an object")

    missing_fields = KNOWLEDGE_FIELDS - set(result)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise KnowledgeInvalidJSONError(f"Knowledge agent JSON is missing fields: {missing}")

    confidence = result["knowledge_confidence"]
    if not isinstance(confidence, dict):
        raise KnowledgeInvalidJSONError("Knowledge agent knowledge_confidence must be an object")

    missing_confidence_fields = KNOWLEDGE_CONFIDENCE_FIELDS - set(confidence)
    if missing_confidence_fields:
        missing = ", ".join(sorted(missing_confidence_fields))
        raise KnowledgeInvalidJSONError(
            f"Knowledge agent knowledge_confidence is missing fields: {missing}"
        )

    return result


def generate_knowledge(discovery: dict[str, Any]) -> dict[str, Any]:
    if not discovery:
        raise KnowledgeAgentError("Approved discovery output cannot be empty")

    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": KNOWLEDGE_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(discovery)},
            ],
            response_format={"type": "json_object"},
        )
    except APITimeoutError as exc:
        raise KnowledgeTimeoutError("Azure OpenAI request timed out") from exc
    except OpenAIError as exc:
        raise KnowledgeAzureError(f"Azure OpenAI request failed: {exc}") from exc
    except Exception as exc:
        raise KnowledgeAgentError(f"Unexpected knowledge error: {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise KnowledgeInvalidJSONError("Knowledge agent returned an empty response")

    return _parse_knowledge_json(content)
