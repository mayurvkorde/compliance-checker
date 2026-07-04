from typing import Dict, List, Optional

from app.schemas import ComplianceReport, ConflictingPolicy

_NO_CONFLICT_ACTION = "No changes required; existing policies comply with the regulation."

def assemble_report(
    regulation_id: str,
    policy_verdicts: List[Dict],
    trace_id: Optional [str] = None,
) -> ComplianceReport:
    """Combine per-policy verdicts into the final structured report.
    Args:
        regulation_id: The regulation being checked.
        policy_verdicts: list of (policy_id, violates, reason, recommended_action).
        trace_id: Observability trace id to embed in the output.
    """
    conflicting_policies = [
        ConflictingPolicy(policy_id=verdict["policy_id"], reason=verdict["reason"])
        for verdict in policy_verdicts
        if verdict.get("violates")
    ]
    recommended_actions = [
        verdict["recommended_action"]
        for verdict in policy_verdicts
        if verdict.get("violates") and verdict.get("recommended_action")
    ]
    recommended_action = (
        " ".join(recommended_actions) if recommended_actions else _NO_CONFLICT_ACTION
    )
    return ComplianceReport(
        target_regulation=regulation_id,
        conflict_detected=len(conflicting_policies) > 0,
        conflicting_policies=conflicting_policies,
        recommended_action=recommended_action,
        trace_id=trace_id,
    )