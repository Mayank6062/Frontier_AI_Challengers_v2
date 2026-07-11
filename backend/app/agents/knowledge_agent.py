import json
import os
from pathlib import Path
from typing import Any
 
from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError
 
from app.prompts.knowledge_prompt import KNOWLEDGE_SYSTEM_PROMPT
 
 
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
 
 
KNOWLEDGE_FIELDS = {
    "knowledge_retrieval",
    "enterprise_standards",
    "best_practices",
    "reference_architectures",
    "technology_catalog",
    "compliance_standards",
    "previous_approved_solutions",
    "knowledge_confidence",
}
 
 
KNOWLEDGE_CONFIDENCE_FIELDS = {
    "overall_confidence",
    "knowledge_completeness",
    "risk_level",
    "recommendation",
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
        timeout=120.0,
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
 
 
def _build_knowledge_display_data(agent_data: dict[str, Any]) -> dict[str, Any]:
    """Build UI-optimized display_data from knowledge agent_data."""
   
    sections: list[dict[str, Any]] = []
 
    # 1 — Knowledge Retrieval
    retrieval = agent_data.get("knowledge_retrieval", {})
    if isinstance(retrieval, dict) and retrieval:
        content_list = retrieval.get("content", [])
        sections.append({
            "heading": retrieval.get("title", "Knowledge Retrieval"),
            "type": "knowledge_summary",
            "business_summary": retrieval.get("business_summary", ""),
            "content": content_list if isinstance(content_list, list) else [],
        })
 
    # 2 — Enterprise Standards
    standards_section = agent_data.get("enterprise_standards", {})
    if isinstance(standards_section, dict) and standards_section:
        standards_list = standards_section.get("standards", [])
        sections.append({
            "heading": standards_section.get("title", "Enterprise Standards"),
            "type": "objects_list",
            "business_summary": standards_section.get("business_summary", ""),
            "items": standards_list if isinstance(standards_list, list) else [],
        })
 
    # 3 — Best Practices
    practices_section = agent_data.get("best_practices", {})
    if isinstance(practices_section, dict) and practices_section:
        practices_list = practices_section.get("practices", [])
        sections.append({
            "heading": practices_section.get("title", "Best Practices"),
            "type": "objects_list",
            "business_summary": practices_section.get("business_summary", ""),
            "items": practices_list if isinstance(practices_list, list) else [],
        })
 
    # 4 — Reference Architectures
    archs_section = agent_data.get("reference_architectures", {})
    if isinstance(archs_section, dict) and archs_section:
        archs_list = archs_section.get("architectures", [])
        sections.append({
            "heading": archs_section.get("title", "Reference Architectures"),
            "type": "objects_list",
            "business_summary": archs_section.get("business_summary", ""),
            "items": archs_list if isinstance(archs_list, list) else [],
        })
 
    # 5 — Technology Catalog
    tech_section = agent_data.get("technology_catalog", {})
    if isinstance(tech_section, dict) and tech_section:
        tech_list = tech_section.get("technologies", [])
        sections.append({
            "heading": tech_section.get("title", "Technology Catalog"),
            "type": "objects_list",
            "business_summary": tech_section.get("business_summary", ""),
            "items": tech_list if isinstance(tech_list, list) else [],
        })
 
    # 6 — Compliance Standards
    compliance_section = agent_data.get("compliance_standards", {})
    if isinstance(compliance_section, dict) and compliance_section:
        compliance_list = compliance_section.get("standards", [])
        sections.append({
            "heading": compliance_section.get("title", "Compliance Standards"),
            "type": "objects_list",
            "business_summary": compliance_section.get("business_summary", ""),
            "items": compliance_list if isinstance(compliance_list, list) else [],
        })
 
    # 7 — Previous Approved Solutions
    solutions_section = agent_data.get("previous_approved_solutions", {})
    if isinstance(solutions_section, dict) and solutions_section:
        solutions_list = solutions_section.get("solutions", [])
        sections.append({
            "heading": solutions_section.get("title", "Previous Approved Solutions"),
            "type": "objects_list",
            "business_summary": solutions_section.get("business_summary", ""),
            "items": solutions_list if isinstance(solutions_list, list) else [],
        })
 
    # 8 — Knowledge Confidence
    confidence = agent_data.get("knowledge_confidence", {})
    if isinstance(confidence, dict) and confidence:
        sections.append({
            "heading": confidence.get("title", "Knowledge Confidence"),
            "type": "confidence",
            "business_summary": confidence.get("business_summary", ""),
            "overall_confidence": confidence.get("overall_confidence", "Not assessed"),
            "knowledge_completeness": confidence.get("knowledge_completeness", "Not assessed"),
            "risk_level": confidence.get("risk_level", "Not assessed"),
            "recommendation": confidence.get("recommendation", ""),
        })
 
    return {
        "title": "Enterprise Knowledge Report",
        "subtitle": "Knowledge enrichment based on approved discovery",
        "sections": sections,
    }
 
 
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
 
    agent_data = _parse_knowledge_json(content)
    display_data = _build_knowledge_display_data(agent_data)
   
    return {
        "agent_data": agent_data,
        "display_data": display_data,
    }
 