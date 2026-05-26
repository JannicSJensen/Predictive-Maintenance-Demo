from __future__ import annotations

from typing import Any, Dict, List

from src.agents.base import Agent
from src.models.recommendations import EvaluationScore, Recommendation, SafetyDecision


class EvaluationAgent(Agent):
    name = "evaluation_agent"
    description = "Scores recommendation quality for demo explainability"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        recommendations: List[Recommendation] = context.get("recommendations", [])
        safety_decisions: List[SafetyDecision] = context.get("safety_decisions", [])
        safety_by_id = {d.recommendation_id: d.decision for d in safety_decisions}

        scores: List[EvaluationScore] = []
        for recommendation in recommendations:
            decision = safety_by_id.get(recommendation.id, "needs_approval")
            score = self._score_recommendation(recommendation, decision)
            scores.append(score)

        return {
            "agent": self.name,
            "scores": scores,
        }

    @staticmethod
    def _score_recommendation(recommendation: Recommendation, safety_decision: str) -> EvaluationScore:
        groundedness = min(5, max(1, len(recommendation.evidence)))
        usefulness = 4 if recommendation.type in {"automation", "energy", "climate"} else 3
        safety = 5 if safety_decision == "approved" else 3 if safety_decision == "needs_approval" else 1
        reversibility = 5 if recommendation.risk_level == "low" else 3
        confidence = min(5, max(2, groundedness + (1 if recommendation.risk_level == "low" else 0)))

        explanation = (
            f"Evidence points: {len(recommendation.evidence)}; "
            f"safety decision: {safety_decision}; "
            f"risk level: {recommendation.risk_level}."
        )

        return EvaluationScore(
            recommendation_id=recommendation.id,
            groundedness=groundedness,
            usefulness=usefulness,
            safety=safety,
            reversibility=reversibility,
            confidence=confidence,
            explanation=explanation,
        )
