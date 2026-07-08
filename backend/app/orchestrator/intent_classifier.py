from __future__ import annotations

from typing import Literal

Intent = Literal[
    "START_WORKFLOW",
    "CONTINUE",
    "REQUIREMENT_CHANGE",
    "CLARIFICATION_ANSWER",
    "QUESTION",
    "EXPLAIN",
    "REGENERATE",
    "GENERATE_OUTPUT",
    "STOP",
    "UNKNOWN",
]


def classify_intent(message: str) -> Intent:
    if not message:
        return "UNKNOWN"

    m = message.lower().strip()

    # Start intents
    if any(p in m for p in ("start", "begin", "new workflow", "run workflow")):
        return "START_WORKFLOW"

    # Continue variants
    if any(p in m for p in ("continue", "proceed", "next", "go ahead", "looks good", "approved", "approve", "yes")):
        return "CONTINUE"

    # Output generation
    if any(p in m for p in ("generate final", "generate html", "final report", "generate report", "generate output", "export html")):
        return "GENERATE_OUTPUT"

    # Regenerate current stage
    if any(p in m for p in ("regenerate", "retry", "rerun", "re-generate")):
        return "REGENERATE"

    # Clarification answers often contain numeric metrics or explicit clarifying content
    if any(p in m for p in ("tb/day", "tb/day", "requests/sec", "qps", "peak", "peak load", "concurrent", "throughput")) or any(char.isdigit() for char in m):
        return "CLARIFICATION_ANSWER"

    # Requirement change — technology/cloud/platform keywords
    if any(p in m for p in ("use aws", "use azure", "use gcp", "kubernetes", "k8s", "redis", "postgres", "mysql", "mongodb", "kafka", "rabbitmq")):
        return "REQUIREMENT_CHANGE"

    # Explain intent
    if m.startswith("explain") or m.startswith("explain this") or "explain" in m:
        return "EXPLAIN"

    # Question
    if m.endswith("?") or any(p in m for p in ("why", "how", "what", "where", "when")):
        return "QUESTION"

    # Stop
    if any(p in m for p in ("stop", "cancel", "halt")):
        return "STOP"

    return "UNKNOWN"
