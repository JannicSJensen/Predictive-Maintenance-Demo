from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, Field

    PYDANTIC_AVAILABLE = True
except ImportError:  # pragma: no cover
    from dataclasses import dataclass, field

    PYDANTIC_AVAILABLE = False


if PYDANTIC_AVAILABLE:

    class Recommendation(BaseModel):
        id: str
        agent_name: str
        type: str
        title: str
        rationale: str
        evidence: List[str] = Field(default_factory=list)
        risk_level: str
        requires_approval: bool
        proposed_action: Optional[Dict[str, Any]] = None
        yaml: Optional[str] = None

    class SafetyDecision(BaseModel):
        recommendation_id: str
        decision: str
        reason: str
        required_user_confirmation: Optional[str] = None
        safer_alternative: Optional[str] = None

    class EvaluationScore(BaseModel):
        recommendation_id: str
        groundedness: int
        usefulness: int
        safety: int
        reversibility: int
        confidence: int
        explanation: str

else:

    @dataclass
    class Recommendation:
        id: str
        agent_name: str
        type: str
        title: str
        rationale: str
        evidence: List[str] = field(default_factory=list)
        risk_level: str = "low"
        requires_approval: bool = True
        proposed_action: Optional[Dict[str, Any]] = None
        yaml: Optional[str] = None

    @dataclass
    class SafetyDecision:
        recommendation_id: str
        decision: str
        reason: str
        required_user_confirmation: Optional[str] = None
        safer_alternative: Optional[str] = None

    @dataclass
    class EvaluationScore:
        recommendation_id: str
        groundedness: int
        usefulness: int
        safety: int
        reversibility: int
        confidence: int
        explanation: str
