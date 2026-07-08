import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError

from app.prompts.recommendation_prompt import RECOMMENDATION_SYSTEM_PROMPT


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


RECOMMENDATION_FIELDS = {
    "architecture_pattern_recommendation",
    "technology_recommendation",
    "cloud_recommendation",
    "build_vs_buy_analysis",
    "data_flow_recommendation",
    "integration_recommendation",
    "security_recommendation",
    "architecture_simplification",
    "cost_recommendation",
    "risk_recommendation",
    "architecture_candidate_generation",
    "architecture_scoring",
}


ARCHITECTURE_SCORING_FIELDS = {
    "recommended_candidate",
    "scores",
}


class RecommendationAgentError(RuntimeError):
    pass


class RecommendationInvalidJSONError(RecommendationAgentError):
    pass


class RecommendationAzureError(RecommendationAgentError):
    pass


class RecommendationTimeoutError(RecommendationAgentError):
    pass


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RecommendationAgentError(f"Missing required environment variable: {name}")
    return value


def _create_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=_get_required_env("AZURE_OPENAI_API_KEY"),
        azure_endpoint=_get_required_env("AZURE_OPENAI_ENDPOINT"),
        api_version=_get_required_env("AZURE_OPENAI_API_VERSION"),
        timeout=60.0,
    )


def _parse_recommendation_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RecommendationInvalidJSONError("Recommendation agent returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise RecommendationInvalidJSONError("Recommendation agent JSON must be an object")

    missing_fields = RECOMMENDATION_FIELDS - set(result)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise RecommendationInvalidJSONError(
            f"Recommendation agent JSON is missing fields: {missing}"
        )

    scoring = result["architecture_scoring"]
    if not isinstance(scoring, dict):
        raise RecommendationInvalidJSONError("Recommendation architecture_scoring must be an object")

    missing_scoring_fields = ARCHITECTURE_SCORING_FIELDS - set(scoring)
    if missing_scoring_fields:
        missing = ", ".join(sorted(missing_scoring_fields))
        raise RecommendationInvalidJSONError(
            f"Recommendation architecture_scoring is missing fields: {missing}"
        )

    return result


def generate_recommendation(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
) -> dict[str, Any]:
    if not discovery:
        raise RecommendationAgentError("Approved discovery output cannot be empty")
    if not knowledge:
        raise RecommendationAgentError("Approved knowledge output cannot be empty")

    payload = {
        "discovery": discovery,
        "knowledge": knowledge,
    }

    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": RECOMMENDATION_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)},
            ],
            response_format={"type": "json_object"},
        )
    except APITimeoutError as exc:
        raise RecommendationTimeoutError("Azure OpenAI request timed out") from exc
    except OpenAIError as exc:
        raise RecommendationAzureError(f"Azure OpenAI request failed: {exc}") from exc
    except Exception as exc:
        raise RecommendationAgentError(f"Unexpected recommendation error: {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise RecommendationInvalidJSONError("Recommendation agent returned an empty response")

    return _parse_recommendation_json(content)
