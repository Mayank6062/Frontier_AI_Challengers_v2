import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError

from app.prompts.validation_prompt import VALIDATION_SYSTEM_PROMPT


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


# ─── Top-level required keys ───────────────────────────────────────────────────

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

# ─── Architecture review keys (now an object, not a string) ───────────────────

ARCHITECTURE_REVIEW_FIELDS = {
    "executive_assessment",
    "business_alignment",
    "technical_readiness",
    "production_readiness",
    "governance_readiness",
    "overall_verdict",
}

# ─── Best practice item fields ────────────────────────────────────────────────

BEST_PRACTICE_ITEM_FIELDS = {
    "practice",
    "status",
    "assessment",
    "why_it_matters",
    "recommendation",
    "expected_benefit",
    "risk_level",
}

# ─── Compliance item fields ───────────────────────────────────────────────────

COMPLIANCE_ITEM_FIELDS = {
    "framework",
    "status",
    "purpose",
    "current_assessment",
    "evidence",
    "recommendation",
    "business_impact",
}

# ─── Structured sub-object fields (used by security / perf / scale / rel / obs) ─

DETAIL_CARD_FIELDS = {"assessment", "why_it_matters", "recommendation", "expected_outcome"}

SECURITY_KEYS = {"authentication", "authorization", "encryption", "secrets", "iam", "network_security", "api_security"}
PERFORMANCE_KEYS = {"latency", "throughput", "caching", "database_performance"}
SCALABILITY_KEYS = {"horizontal_scaling", "vertical_scaling", "auto_scaling", "elasticity"}
RELIABILITY_KEYS = {"high_availability", "disaster_recovery", "backup_strategy", "fault_tolerance"}
OBSERVABILITY_KEYS = {"logging", "monitoring", "tracing", "alerting", "dashboards"}

# ─── Cost validation fields ───────────────────────────────────────────────────

COST_FIELDS = {"estimated_cost", "optimization_opportunities", "resource_utilization"}

# ─── Risk item fields ─────────────────────────────────────────────────────────

RISK_ITEM_FIELDS = {
    "risk", "severity", "business_impact", "likelihood",
    "mitigation", "owner", "priority", "expected_resolution",
}

RISK_VALIDATION_FIELDS = {"high_risks", "medium_risks", "low_risks", "mitigation_suggestions"}

# ─── Score fields ─────────────────────────────────────────────────────────────

SCORE_FIELDS = {
    "overall_score", "overall_rationale",
    "security", "security_rationale",
    "performance", "performance_rationale",
    "scalability", "scalability_rationale",
    "maintainability", "maintainability_rationale",
    "reliability", "reliability_rationale",
    "cost", "cost_rationale",
    "compliance", "compliance_rationale",
}

FINAL_RECOMMENDATIONS = {
    "Approved",
    "Approved With Recommendations",
    "Requires Revision",
    "Rejected",
}


# ─── Custom exceptions ────────────────────────────────────────────────────────

class ValidationAgentError(RuntimeError):
    pass

class ValidationInvalidJSONError(ValidationAgentError):
    pass

class ValidationAzureError(ValidationAgentError):
    pass

class ValidationTimeoutError(ValidationAgentError):
    pass


# ─── Environment / client helpers ─────────────────────────────────────────────

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
        timeout=180.0,
    )


# ─── Score interpretation ─────────────────────────────────────────────────────

def _interpret_score(score: int) -> str:
    if score >= 90:
        return "Excellent — Production Ready"
    elif score >= 75:
        return "Good — Approved with Recommendations"
    elif score >= 60:
        return "Adequate — Requires Revision"
    return "Insufficient — Not Recommended"


def _score_color(score: int) -> str:
    if score >= 90:
        return "success"
    elif score >= 75:
        return "info"
    elif score >= 60:
        return "warning"
    return "error"


# ─── Validation helpers ───────────────────────────────────────────────────────

def _validate_object_fields(result: dict[str, Any], field: str, expected: set[str]) -> None:
    value = result[field]
    if not isinstance(value, dict):
        raise ValidationInvalidJSONError(f"Validation {field} must be an object")
    missing = expected - set(value)
    if missing:
        raise ValidationInvalidJSONError(
            f"Validation {field} is missing fields: {', '.join(sorted(missing))}"
        )


def _validate_detail_card_keys(section: dict[str, Any], section_name: str, required_keys: set[str]) -> None:
    """Validate that each sub-key of a validation section is a detail-card object."""
    for key in required_keys:
        if key not in section:
            raise ValidationInvalidJSONError(f"{section_name} is missing key: {key}")
        card = section[key]
        if not isinstance(card, dict):
            raise ValidationInvalidJSONError(
                f"{section_name}.{key} must be an object with assessment/why_it_matters/recommendation/expected_outcome"
            )
        missing = DETAIL_CARD_FIELDS - set(card)
        if missing:
            raise ValidationInvalidJSONError(
                f"{section_name}.{key} is missing fields: {', '.join(sorted(missing))}"
            )


def _validate_risk_item(item: Any, list_name: str, idx: int) -> None:
    if not isinstance(item, dict):
        raise ValidationInvalidJSONError(f"{list_name}[{idx}] must be an object")
    missing = RISK_ITEM_FIELDS - set(item)
    if missing:
        raise ValidationInvalidJSONError(
            f"{list_name}[{idx}] is missing fields: {', '.join(sorted(missing))}"
        )


# ─── JSON parsing & schema validation ────────────────────────────────────────

def _parse_validation_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValidationInvalidJSONError("Validation agent returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise ValidationInvalidJSONError("Validation agent JSON must be an object")

    missing_top = VALIDATION_FIELDS - set(result)
    if missing_top:
        raise ValidationInvalidJSONError(
            f"Validation agent JSON is missing fields: {', '.join(sorted(missing_top))}"
        )

    # 1. architecture_review — now an object
    ar = result["architecture_review"]
    if not isinstance(ar, dict):
        raise ValidationInvalidJSONError("architecture_review must be an object")
    missing_ar = ARCHITECTURE_REVIEW_FIELDS - set(ar)
    if missing_ar:
        raise ValidationInvalidJSONError(
            f"architecture_review is missing fields: {', '.join(sorted(missing_ar))}"
        )

    # 2. best_practice_validation
    bp_list = result["best_practice_validation"]
    if not isinstance(bp_list, list):
        raise ValidationInvalidJSONError("best_practice_validation must be an array")
    for i, item in enumerate(bp_list):
        if not isinstance(item, dict):
            raise ValidationInvalidJSONError(f"best_practice_validation[{i}] must be an object")
        missing_bp = BEST_PRACTICE_ITEM_FIELDS - set(item)
        if missing_bp:
            raise ValidationInvalidJSONError(
                f"best_practice_validation[{i}] is missing fields: {', '.join(sorted(missing_bp))}"
            )

    # 3. compliance_validation
    comp_list = result["compliance_validation"]
    if not isinstance(comp_list, list):
        raise ValidationInvalidJSONError("compliance_validation must be an array")
    for i, item in enumerate(comp_list):
        if not isinstance(item, dict):
            raise ValidationInvalidJSONError(f"compliance_validation[{i}] must be an object")
        missing_comp = COMPLIANCE_ITEM_FIELDS - set(item)
        if missing_comp:
            raise ValidationInvalidJSONError(
                f"compliance_validation[{i}] is missing fields: {', '.join(sorted(missing_comp))}"
            )

    # 4–8. Detail-card sections (security / performance / scalability / reliability / observability)
    detail_sections = {
        "security_validation": SECURITY_KEYS,
        "performance_validation": PERFORMANCE_KEYS,
        "scalability_validation": SCALABILITY_KEYS,
        "reliability_validation": RELIABILITY_KEYS,
        "observability_validation": OBSERVABILITY_KEYS,
    }
    for section_name, required_keys in detail_sections.items():
        if not isinstance(result[section_name], dict):
            raise ValidationInvalidJSONError(f"{section_name} must be an object")
        _validate_detail_card_keys(result[section_name], section_name, required_keys)

    # 9. cost_validation
    _validate_object_fields(result, "cost_validation", COST_FIELDS)
    if not isinstance(result["cost_validation"].get("optimization_opportunities"), list):
        raise ValidationInvalidJSONError("cost_validation.optimization_opportunities must be an array")

    # 10. risk_validation
    risk = result["risk_validation"]
    if not isinstance(risk, dict):
        raise ValidationInvalidJSONError("risk_validation must be an object")
    missing_risk = RISK_VALIDATION_FIELDS - set(risk)
    if missing_risk:
        raise ValidationInvalidJSONError(
            f"risk_validation is missing fields: {', '.join(sorted(missing_risk))}"
        )
    for list_name in ("high_risks", "medium_risks", "low_risks"):
        if not isinstance(risk[list_name], list):
            raise ValidationInvalidJSONError(f"risk_validation.{list_name} must be an array")
        for i, item in enumerate(risk[list_name]):
            _validate_risk_item(item, f"risk_validation.{list_name}", i)
    if not isinstance(risk["mitigation_suggestions"], list):
        raise ValidationInvalidJSONError("risk_validation.mitigation_suggestions must be an array")

    # 11. architecture_score
    _validate_object_fields(result, "architecture_score", SCORE_FIELDS)

    # 12. final_recommendation
    if result["final_recommendation"] not in FINAL_RECOMMENDATIONS:
        raise ValidationInvalidJSONError(
            f"final_recommendation must be one of: {', '.join(sorted(FINAL_RECOMMENDATIONS))}"
        )

    return result


# ─── Display-data builders ────────────────────────────────────────────────────

def _build_architecture_review_cards(ar: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert the 6-key architecture_review object into executive assessment cards."""
    label_map = {
        "executive_assessment": ("🎯 Executive Assessment", "summary"),
        "business_alignment":   ("📋 Business Alignment",  "alignment"),
        "technical_readiness":  ("⚙️ Technical Readiness", "readiness"),
        "production_readiness": ("🚀 Production Readiness","production"),
        "governance_readiness": ("🛡️ Governance Readiness","governance"),
        "overall_verdict":      ("✅ Overall Verdict",      "verdict"),
    }
    cards = []
    for key, (title, card_type) in label_map.items():
        value = ar.get(key, "")
        if value:
            cards.append({"title": title, "type": card_type, "content": value})
    return cards


def _build_best_practice_cards(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map best_practice_validation objects to full UI card shape."""
    if not items:
        return [{
            "title": "Best Practices Assessment",
            "status": "⭕ Not Assessed",
            "assessment": "No best practice data returned. Provide additional architecture specifications for assessment.",
            "why_it_matters": "",
            "recommendation": None,
            "expected_benefit": "",
            "risk_level": None,
        }]
    cards = []
    for item in items:
        if isinstance(item, dict):
            cards.append({
                "title": item.get("practice", "Best Practice"),
                "status": item.get("status", "⭕ Unknown"),
                "assessment": item.get("assessment", ""),
                "why_it_matters": item.get("why_it_matters", ""),
                "recommendation": item.get("recommendation"),
                "expected_benefit": item.get("expected_benefit", ""),
                "risk_level": item.get("risk_level"),
            })
    return cards


def _build_compliance_cards(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map compliance_validation objects to full UI card shape."""
    if not items:
        return [{
            "title": "Compliance Assessment",
            "status": "⭕ Not Assessed",
            "purpose": "Engage compliance team for formal framework assessment.",
            "current_assessment": "",
            "evidence": "",
            "recommendation": None,
            "business_impact": "",
        }]
    cards = []
    for item in items:
        if isinstance(item, dict):
            cards.append({
                "title": item.get("framework", "Compliance Framework"),
                "status": item.get("status", "⭕ Unknown"),
                "purpose": item.get("purpose", ""),
                "current_assessment": item.get("current_assessment", ""),
                "evidence": item.get("evidence", ""),
                "recommendation": item.get("recommendation"),
                "business_impact": item.get("business_impact", ""),
            })
    return cards


def _build_detail_cards(section: dict[str, Any], key_labels: dict[str, str]) -> list[dict[str, Any]]:
    """
    Convert a detail-card section (security / perf / scale / rel / obs) into card list.
    Each sub-object has: assessment, why_it_matters, recommendation, expected_outcome.
    """
    cards = []
    for key, label in key_labels.items():
        sub = section.get(key)
        if not sub:
            continue
        if isinstance(sub, dict):
            cards.append({
                "title": label,
                "assessment": sub.get("assessment", ""),
                "why_it_matters": sub.get("why_it_matters", ""),
                "recommendation": sub.get("recommendation"),
                "expected_outcome": sub.get("expected_outcome", ""),
            })
        elif isinstance(sub, str) and sub.strip():
            # Graceful fallback if model returns old-format string
            cards.append({"title": label, "assessment": sub, "why_it_matters": "", "recommendation": None, "expected_outcome": ""})
    return cards or [{"title": "Assessment", "assessment": "No data returned.", "why_it_matters": "", "recommendation": None, "expected_outcome": ""}]


def _build_risk_register(risk: dict[str, Any]) -> dict[str, Any]:
    """Build a structured executive risk register from risk_validation."""
    def _normalise_risk_list(raw: list[Any]) -> list[dict[str, Any]]:
        normalised = []
        for item in raw:
            if isinstance(item, dict):
                normalised.append({
                    "risk": item.get("risk", "Unspecified risk"),
                    "severity": item.get("severity", "Medium"),
                    "business_impact": item.get("business_impact", ""),
                    "likelihood": item.get("likelihood", "Medium"),
                    "mitigation": item.get("mitigation", ""),
                    "owner": item.get("owner", "Architecture Team"),
                    "priority": item.get("priority", "P2"),
                    "expected_resolution": item.get("expected_resolution", "TBD"),
                })
            elif isinstance(item, str) and item.strip():
                # Graceful fallback for old pipe-delimited format
                normalised.append({
                    "risk": item.split("|")[0].replace("Risk:", "").strip()[:80],
                    "severity": "Medium",
                    "business_impact": "",
                    "likelihood": "Medium",
                    "mitigation": "",
                    "owner": "Architecture Team",
                    "priority": "P2",
                    "expected_resolution": "TBD",
                })
        return normalised

    return {
        "high_risks": _normalise_risk_list(risk.get("high_risks", [])),
        "medium_risks": _normalise_risk_list(risk.get("medium_risks", [])),
        "low_risks": _normalise_risk_list(risk.get("low_risks", [])),
        "mitigation_suggestions": [
            str(s) for s in risk.get("mitigation_suggestions", []) if s
        ],
    }


def _build_scorecard(scores: dict[str, Any]) -> list[dict[str, Any]]:
    """Build enriched scorecard items with rationale for each dimension."""
    dimensions = [
        ("overall_score",    "overall_rationale",    "Overall Score",    True),
        ("security",         "security_rationale",    "Security",         False),
        ("performance",      "performance_rationale", "Performance",      False),
        ("scalability",      "scalability_rationale", "Scalability",      False),
        ("maintainability",  "maintainability_rationale", "Maintainability", False),
        ("reliability",      "reliability_rationale", "Reliability",      False),
        ("cost",             "cost_rationale",        "Cost Optimisation",False),
        ("compliance",       "compliance_rationale",  "Compliance",       False),
    ]
    items = []
    for score_key, rationale_key, label, is_overall in dimensions:
        score = int(scores.get(score_key, 0))
        items.append({
            "label": label,
            "value": score,
            "rating": _interpret_score(score),
            "rationale": scores.get(rationale_key, ""),
            "color": _score_color(score),
            "display": "progress" if is_overall else "score",
        })
    return items


def _build_validation_display_data(validation: dict[str, Any]) -> dict[str, Any]:
    """Assemble the full enterprise display payload from validated agent data."""
    scores = validation.get("architecture_score", {})
    overall_score = int(scores.get("overall_score", 0))
    final_rec = validation.get("final_recommendation", "Pending Review")

    overall_rating = _interpret_score(overall_score)
    decision_color = _score_color(overall_score)
    decision_icon = {
        "success": "✓",
        "info":    "→",
        "warning": "⚠",
        "error":   "✗",
    }.get(decision_color, "→")

    # ── Section-specific label maps ──────────────────────────────────
    security_labels = {
        "authentication":  "🔑 Authentication",
        "authorization":   "🔐 Authorization",
        "encryption":      "🔒 Encryption",
        "secrets":         "🗝️ Secrets Management",
        "iam":             "👤 Identity & Access Management (IAM)",
        "network_security":"🌐 Network Security",
        "api_security":    "🔌 API Security",
    }
    performance_labels = {
        "latency":              "⚡ Latency",
        "throughput":           "📊 Throughput",
        "caching":              "💾 Caching Strategy",
        "database_performance": "🗃️ Database Performance",
    }
    scalability_labels = {
        "horizontal_scaling": "↔ Horizontal Scaling",
        "vertical_scaling":   "↕ Vertical Scaling",
        "auto_scaling":       "⚙️ Auto-Scaling",
        "elasticity":         "🔄 Elasticity",
    }
    reliability_labels = {
        "high_availability": "🏗️ High Availability",
        "disaster_recovery": "🛟 Disaster Recovery (DR)",
        "backup_strategy":   "💽 Backup Strategy",
        "fault_tolerance":   "🔧 Fault Tolerance",
    }
    observability_labels = {
        "logging":    "📝 Logging",
        "monitoring": "📡 Monitoring",
        "tracing":    "🔍 Distributed Tracing",
        "alerting":   "🚨 Alerting",
        "dashboards": "📈 Dashboards",
    }

    return {
        "title": "Enterprise Architecture Review Board Assessment",
        "subtitle": (
            f"Overall Rating: {overall_rating} ({overall_score}/100) "
            f"• Decision: {final_rec}"
        ),
        "sections": [
            {
                "heading": "Architecture Review",
                "type": "executive_cards",
                "items": _build_architecture_review_cards(
                    validation.get("architecture_review", {})
                ),
            },
            {
                "heading": "Best Practice Validation",
                "type": "best_practice_cards",
                "items": _build_best_practice_cards(
                    validation.get("best_practice_validation", [])
                ),
            },
            {
                "heading": "Compliance Validation",
                "type": "compliance_cards",
                "items": _build_compliance_cards(
                    validation.get("compliance_validation", [])
                ),
            },
            {
                "heading": "Security Validation",
                "type": "detail_cards",
                "items": _build_detail_cards(
                    validation.get("security_validation", {}), security_labels
                ),
            },
            {
                "heading": "Cost Validation",
                "type": "cost_card",
                "estimated_cost": validation.get("cost_validation", {}).get("estimated_cost", ""),
                "optimization_opportunities": validation.get("cost_validation", {}).get(
                    "optimization_opportunities", []
                ),
                "resource_utilization": validation.get("cost_validation", {}).get(
                    "resource_utilization", ""
                ),
            },
            {
                "heading": "Performance Validation",
                "type": "detail_cards",
                "items": _build_detail_cards(
                    validation.get("performance_validation", {}), performance_labels
                ),
            },
            {
                "heading": "Scalability Validation",
                "type": "detail_cards",
                "items": _build_detail_cards(
                    validation.get("scalability_validation", {}), scalability_labels
                ),
            },
            {
                "heading": "Reliability Validation",
                "type": "detail_cards",
                "items": _build_detail_cards(
                    validation.get("reliability_validation", {}), reliability_labels
                ),
            },
            {
                "heading": "Observability Validation",
                "type": "detail_cards",
                "items": _build_detail_cards(
                    validation.get("observability_validation", {}), observability_labels
                ),
            },
            {
                "heading": "Risk Validation",
                "type": "risk_register",
                **_build_risk_register(validation.get("risk_validation", {})),
            },
            {
                "heading": "Architecture Score",
                "type": "score_card",
                "items": _build_scorecard(scores),
                "framework": "Azure Well-Architected Framework + TOGAF ADM",
            },
            {
                "heading": "Final Recommendation",
                "type": "alert",
                "content": final_rec,
                "color": decision_color,
                "icon": decision_icon,
                "score": overall_score,
                "rating": overall_rating,
            },
        ],
        "actions": [
            {"label": "Edit Requirements", "action": "edit"},
            {"label": "Approve & Continue to Output", "action": "approve"},
        ],
    }


# ─── Public entry point ────────────────────────────────────────────────────────

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