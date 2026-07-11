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
        timeout=180.0,
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
 
 
def _build_recommendation_display_data(agent_data: dict[str, Any]) -> dict[str, Any]:
    """Build UI-optimized display_data from recommendation agent_data."""
   
    sections: list[dict[str, Any]] = []
   
    # 1 — Architecture Pattern Recommendation
    patterns = agent_data.get("architecture_pattern_recommendation", [])
    if isinstance(patterns, list) and patterns:
        sections.append({
            "heading": "Architecture Pattern Recommendation",
            "type": "pattern_cards",
            "items": patterns,
        })
   
    # 2 — Technology Recommendation
    techs = agent_data.get("technology_recommendation", [])
    if isinstance(techs, list) and techs:
        sections.append({
            "heading": "Technology Recommendation",
            "type": "tech_cards",
            "items": techs,
        })
   
    # 3 — Cloud Recommendation
    cloud = agent_data.get("cloud_recommendation", [])
    if isinstance(cloud, list) and cloud:
        sections.append({
            "heading": "Cloud Recommendation",
            "type": "decision_cards",
            "items": cloud,
        })
   
    # 4 — Build vs Buy
    buildvsbuy = agent_data.get("build_vs_buy_analysis", [])
    if isinstance(buildvsbuy, list) and buildvsbuy:
        sections.append({
            "heading": "Build vs Buy",
            "type": "comparison_cards",
            "items": buildvsbuy,
        })
   
    # 5 — Data Flow Recommendation
    dataflow = agent_data.get("data_flow_recommendation", [])
    if isinstance(dataflow, list) and dataflow:
        sections.append({
            "heading": "Data Flow Recommendation",
            "type": "process_cards",
            "items": dataflow,
        })
   
    # 6 — Integration Recommendation
    integration = agent_data.get("integration_recommendation", [])
    if isinstance(integration, list) and integration:
        sections.append({
            "heading": "Integration Recommendation",
            "type": "integration_cards",
            "items": integration,
        })
   
    # 7 — Security Recommendation
    security = agent_data.get("security_recommendation", [])
    if isinstance(security, list) and security:
        sections.append({
            "heading": "Security Recommendation",
            "type": "security_cards",
            "items": security,
        })
   
    # 8 — Architecture Simplification
    simplification = agent_data.get("architecture_simplification", [])
    if isinstance(simplification, list) and simplification:
        sections.append({
            "heading": "Architecture Simplification",
            "type": "improvement_cards",
            "items": simplification,
        })
   
    # 9 — Cost Recommendation
    cost = agent_data.get("cost_recommendation", [])
    if isinstance(cost, list) and cost:
        sections.append({
            "heading": "Cost Recommendation",
            "type": "optimization_cards",
            "items": cost,
        })
   
    # 10 — Risk Recommendation
    risk = agent_data.get("risk_recommendation", [])
    if isinstance(risk, list) and risk:
        sections.append({
            "heading": "Risk Recommendation",
            "type": "risk_cards",
            "items": risk,
        })
   
    # 11 — Architecture Candidates
    candidates = agent_data.get("architecture_candidate_generation", [])
    if isinstance(candidates, list) and candidates:
        sections.append({
            "heading": "Architecture Candidates",
            "type": "candidate_cards",
            "items": candidates,
        })
   
    # Build architecture scoring section with scores
    scoring = agent_data.get("architecture_scoring", {})
    scores = scoring.get("scores", []) if isinstance(scoring, dict) else []
    if isinstance(scores, list) and scores:
        sections.append({
            "heading": "Architecture Scoring",
            "type": "scoring_cards",
            "recommended_candidate": scoring.get("recommended_candidate", "") if isinstance(scoring, dict) else "",
            "items": scores,
        })
   
    return {
        "title": "Enterprise Recommendation Report",
        "subtitle": "Consultant-grade recommendations based on approved discovery and knowledge",
        "sections": sections,
    }