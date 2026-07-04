from typing import List, Optional, Literal

from pydantic import BaseModel, Field

class PolicyVerdict(BaseModel):
    """Structured auditor verdict for ONE policy vs the regulation (Step 2 output)."""
    violates: bool = Field(
        description="True if this policy conflicts with / falls short of the regulation."
    )
    reason: str = Field(
        description="Concise explanation of the conflict (or why the policy complies)."
    )
    recommended_action: str = Field(
        default="",
        description="If it violates, how to amend the policy to comply; otherwise empty.",
    )

class PolicyState(BaseModel):
    policy_name: Optional[Literal["policy_001","policy_002","policy_003"]] = Field(
        default=None,
        description="""Unique identifier of the company policy being evaluated.
            Must be one of: 'policy_001', 'policy_002', or 'policy_003'.
            Return null if no policy is applicable.""",
    )
    policy_text: str = Field(
        description=(
            """Complete text content of the selected company policy exactly as provided
            in the input. Do not summarize, paraphrase, or modify the policy text."""
        )
    )

class ConflictingPolicy (BaseModel):
    policy_id: str
    reason: str

class ComplianceReport(BaseModel):
    """Final structured verification output."""
    target_regulation: str
    conflict_detected: bool
    conflicting_policies: List[ConflictingPolicy]
    recommended_action: str
    trace_id: Optional [str] = None