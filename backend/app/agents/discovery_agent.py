import json
import os
from pathlib import Path
from typing import Any
 
from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError
 
from app.prompts.discovery_prompt import DISCOVERY_SYSTEM_PROMPT
 
 
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
 
 
DISCOVERY_FIELDS = {
    "requirement_intelligence",
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
        timeout=300.0,
    )
 
 
def _parse_discovery_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise DiscoveryInvalidJSONError("Discovery agent returned invalid JSON") from exc
 
    if not isinstance(result, dict):
        raise DiscoveryInvalidJSONError("Discovery agent JSON must be an object")
 
    # New format: LLM returns agent_data + display_data
    if "agent_data" in result and isinstance(result["agent_data"], dict):
        agent_data = result["agent_data"]
    else:
        # Fallback: treat entire result as agent_data (legacy format)
        agent_data = result
 
    missing_fields = DISCOVERY_FIELDS - set(agent_data)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise DiscoveryInvalidJSONError(f"Discovery agent JSON is missing fields: {missing}")
 
    dsa_validation = agent_data.get("dsa_validation", {})
    if not isinstance(dsa_validation, dict):
        raise DiscoveryInvalidJSONError("Discovery agent dsa_validation must be an object")
 
    missing_dsa_fields = DSA_VALIDATION_FIELDS - set(dsa_validation)
    if missing_dsa_fields:
        missing = ", ".join(sorted(missing_dsa_fields))
        raise DiscoveryInvalidJSONError(f"Discovery agent dsa_validation is missing fields: {missing}")
 
    return agent_data
 
 
def _build_discovery_display_data(agent_data: dict[str, Any]) -> dict[str, Any]:
    """Build UI-optimized display_data from agent_data with robust fallback handling."""
   
    sections: list[dict[str, Any]] = []
 
    # 1 — Requirement Intelligence (narrative + summary boxes)
    req_intel = agent_data.get("requirement_intelligence", {})
    if isinstance(req_intel, dict):
        intel_title = req_intel.get("title", "").strip() or "Requirement Intelligence"
        intel_summary = req_intel.get("business_summary", "").strip()
        intel_sections = req_intel.get("sections", [])
       
        if not intel_summary and not intel_sections:
            intel_summary = req_intel.get("subtitle", "").strip() or "Executive summary of discovered requirements"
       
        sections.append({
            "heading": intel_title,
            "type": "requirement_intelligence",
            "content": intel_summary or "Executive summary available",
            "detailed_sections": intel_sections if isinstance(intel_sections, list) else [],
        })
 
    # 2 — Requirement Extraction (professional narrative)
    req_extract = agent_data.get("requirement_extraction", {})
    if isinstance(req_extract, dict):
        extract_title = req_extract.get("title", "").strip() or "Requirement Extraction"
        extract_summary = req_extract.get("business_summary", "").strip()
        extract_analysis = req_extract.get("analysis", [])
       
        if not extract_summary and not extract_analysis:
            extract_summary = req_extract.get("subtitle", "").strip() or "Comprehensive analysis of core requirements"
       
        sections.append({
            "heading": extract_title,
            "type": "requirement_extraction",
            "content": extract_summary or "Requirement analysis available",
            "analysis_items": extract_analysis if isinstance(extract_analysis, list) else [],
        })
 
    # 3 — Functional Requirements (checklist with badges)
    f_reqs = agent_data.get("functional_requirements", {})
    if isinstance(f_reqs, dict):
        f_title = f_reqs.get("title", "").strip() or "Functional Requirements"
        f_summary = f_reqs.get("business_summary", "").strip()
        reqs_list = f_reqs.get("requirements", [])
       
        if not isinstance(reqs_list, list):
            reqs_list = []
        if not f_summary:
            f_summary = f"{len(reqs_list)} functional requirements identified" if reqs_list else "Functional capabilities specified"
       
        sections.append({
            "heading": f_title,
            "type": "checklist",
            "content": f_summary,
            "items": [
                {
                    "id": req.get("id", f"FR-{str(idx+1).zfill(3)}"),
                    "title": req.get("title", "Requirement").strip() or f"Requirement {idx+1}",
                    "description": req.get("description", "").strip() or "To be specified",
                    "priority": req.get("priority", "Medium"),
                    "business_value": req.get("business_value", "").strip() or "Business value to be determined",
                }
                for idx, req in enumerate(reqs_list)
            ] if reqs_list else [],
        })
 
    # 4 — Non-Functional Requirements (enterprise table)
    nf_reqs = agent_data.get("non_functional_requirements", {})
    if isinstance(nf_reqs, dict):
        nf_title = nf_reqs.get("title", "").strip() or "Non-Functional Requirements"
        nf_summary = nf_reqs.get("business_summary", "").strip()
        nf_list = nf_reqs.get("requirements", [])
       
        if not isinstance(nf_list, list):
            nf_list = []
        if not nf_summary:
            nf_summary = "Enterprise-grade quality standards" if nf_list else "Quality standards specified"
       
        sections.append({
            "heading": nf_title,
            "type": "table",
            "content": nf_summary,
            "columns": ["Category", "Requirement", "Target", "Priority"],
            "rows": [
                [
                    nf.get("category", "General").strip() or "General",
                    nf.get("requirement", "Requirement").strip() or "Requirement to be specified",
                    nf.get("target", "Target to be defined").strip() or "Target to be defined",
                    nf.get("priority", "Medium"),
                ]
                for nf in nf_list
            ] if nf_list else [],
        })
 
    # 5 — Business Goals (business cards)
    b_goals = agent_data.get("business_goals", {})
    if isinstance(b_goals, dict):
        b_title = b_goals.get("title", "").strip() or "Business Goals"
        b_summary = b_goals.get("business_summary", "").strip()
        goals_list = b_goals.get("goals", [])
       
        if not isinstance(goals_list, list):
            goals_list = []
        if not b_summary:
            b_summary = "Strategic outcomes expected" if goals_list else "Business goals identified"
       
        sections.append({
            "heading": b_title,
            "type": "cards",
            "content": b_summary,
            "items": [
                {
                    "title": goal.get("goal", "Goal").strip() or f"Goal {idx+1}",
                    "icon": "target",
                    "metadata": [
                        {"label": "Business Impact", "value": goal.get("business_impact", "").strip() or "Impact to be assessed"},
                        {"label": "Success Measure", "value": goal.get("success_measure", "").strip() or "Metrics to be defined"},
                        {"label": "Priority", "value": goal.get("priority", "Medium"), "type": "badge"},
                    ],
                }
                for idx, goal in enumerate(goals_list)
            ] if goals_list else [],
        })
 
    # 6 — Constraints (constraint cards)
    constraints = agent_data.get("constraints", {})
    if isinstance(constraints, dict):
        c_title = constraints.get("title", "").strip() or "Constraints"
        c_summary = constraints.get("business_summary", "").strip()
        const_list = constraints.get("constraints", [])
       
        if not isinstance(const_list, list):
            const_list = []
        if not c_summary:
            c_summary = "Key constraints guide decisions" if const_list else "Constraints identified"
       
        sections.append({
            "heading": c_title,
            "type": "cards",
            "content": c_summary,
            "items": [
                {
                    "title": const.get("constraint", "Constraint").strip() or f"Constraint {idx+1}",
                    "icon": "alert-circle",
                    "metadata": [
                        {"label": "Impact", "value": const.get("impact", "").strip() or "Impact to be assessed"},
                        {"label": "Recommendation", "value": const.get("recommendation", "").strip() or "Approach to be determined"},
                    ],
                }
                for idx, const in enumerate(const_list)
            ] if const_list else [],
        })
 
    # 7 — Assumptions (assumption cards)
    assumptions = agent_data.get("assumptions", {})
    if isinstance(assumptions, dict):
        a_title = assumptions.get("title", "").strip() or "Assumptions"
        a_summary = assumptions.get("business_summary", "").strip()
        assume_list = assumptions.get("assumptions", [])
       
        if not isinstance(assume_list, list):
            assume_list = []
        if not a_summary:
            a_summary = "Key assumptions underlying requirement" if assume_list else "Assumptions identified"
       
        sections.append({
            "heading": a_title,
            "type": "cards",
            "content": a_summary,
            "items": [
                {
                    "title": assume.get("assumption", "Assumption").strip() or f"Assumption {idx+1}",
                    "icon": "info",
                    "metadata": [
                        {"label": "Reason", "value": assume.get("reason", "").strip() or "Reason to be determined"},
                        {"label": "Risk if Invalid", "value": assume.get("risk_if_invalid", "").strip() or "Risk to be assessed", "type": "alert"},
                    ],
                }
                for idx, assume in enumerate(assume_list)
            ] if assume_list else [],
        })
 
    # 8 — Ambiguity Detection (alert cards with risk levels)
    ambiguities = agent_data.get("ambiguities", {})
    if isinstance(ambiguities, dict):
        amb_title = ambiguities.get("title", "").strip() or "Ambiguity Detection"
        amb_summary = ambiguities.get("business_summary", "").strip()
        ambi_list = ambiguities.get("ambiguities", [])
       
        if not isinstance(ambi_list, list):
            ambi_list = []
        if not amb_summary:
            amb_summary = f"{len(ambi_list)} ambiguities detected" if ambi_list else "Gaps requiring clarification"
       
        sections.append({
            "heading": amb_title,
            "type": "alerts",
            "content": amb_summary,
            "items": [
                {
                    "title": ambi.get("issue", "Issue").strip() or f"Ambiguity {idx+1}",
                    "level": ambi.get("risk_level", "Medium"),
                    "description": ambi.get("why_it_matters", "").strip() or "Business impact to be assessed",
                    "metadata": [
                        {"label": "Potential Risk", "value": ambi.get("potential_risk", "").strip() or "Risk to be determined"},
                        {"label": "Recommended Clarification", "value": ambi.get("recommended_clarification", "").strip() or "Clarification approach needed"},
                        {"label": "Risk Level", "value": ambi.get("risk_level", "Medium"), "type": "badge"},
                    ],
                }
                for idx, ambi in enumerate(ambi_list)
            ] if ambi_list else [],
        })
 
    # 9 — Clarification Questions (interview-style questions)
    questions = agent_data.get("clarification_questions", {})
    if isinstance(questions, dict):
        q_title = questions.get("title", "").strip() or "Clarification Questions"
        q_summary = questions.get("business_summary", "").strip()
        q_list = questions.get("questions", [])
       
        if not isinstance(q_list, list):
            q_list = []
        if not q_summary:
            q_summary = f"{len(q_list)} critical questions" if q_list else "Questions for stakeholder interviews"
       
        sections.append({
            "heading": q_title,
            "type": "questions",
            "content": q_summary,
            "items": [
                {
                    "question": q.get("question", "Question?").strip() or f"Question {idx+1}",
                    "reason": q.get("reason", "").strip() or "Reason for question to be determined",
                    "expected_outcome": q.get("expected_business_outcome", "").strip() or "Expected outcome to be clarified",
                    "priority": q.get("priority", "Medium"),
                }
                for idx, q in enumerate(q_list)
            ] if q_list else [],
        })
 
    return {
        "title": "Enterprise Requirement Discovery Report",
        "subtitle": "Production-Ready Discovery for Enterprise Architecture Review",
        "sections": sections,
    }
 
 
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
 
    agent_data = _parse_discovery_json(content)
 
    display_data = _build_discovery_display_data(agent_data)
   
    # DEBUG: Log display_data structure
    print("\n🔍 DISCOVERY DISPLAY_DATA STRUCTURE:")
    print(f"   Title: {display_data.get('title')}")
    print(f"   Sections: {len(display_data.get('sections', []))}")
    for i, section in enumerate(display_data.get('sections', [])):
        print(f"     [{i}] heading={section.get('heading')}, type={section.get('type')}, has_items={bool(section.get('items'))}")
 
    return {
        "agent_data": agent_data,
        "display_data": display_data,
    }