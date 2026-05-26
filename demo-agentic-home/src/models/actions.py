from __future__ import annotations

from typing import List

try:
    from pydantic import BaseModel, Field

    PYDANTIC_AVAILABLE = True
except ImportError:  # pragma: no cover
    from dataclasses import dataclass, field

    PYDANTIC_AVAILABLE = False


if PYDANTIC_AVAILABLE:

    class FinalAction(BaseModel):
        recommendation_id: str
        decision: str
        staged: bool = True

    class FinalActionPlan(BaseModel):
        actions: List[FinalAction] = Field(default_factory=list)

else:

    @dataclass
    class FinalAction:
        recommendation_id: str
        decision: str
        staged: bool = True

    @dataclass
    class FinalActionPlan:
        actions: List[FinalAction] = field(default_factory=list)
