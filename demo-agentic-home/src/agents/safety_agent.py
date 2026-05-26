from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from src.agents.base import Agent
from src.models.recommendations import Recommendation, SafetyDecision


class SafetyAgent(Agent):
    name = "safety_agent"
    description = "Applies guardrails before any recommendation can be executed"

    def __init__(self, policy_path: Path) -> None:
        with policy_path.open("r", encoding="utf-8") as f:
            self.policy = yaml.safe_load(f)

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        recommendations: List[Recommendation] = context.get("recommendations", [])
        decisions: List[SafetyDecision] = []

        for recommendation in recommendations:
            decision = self._review_recommendation(recommendation)
            decisions.append(decision)

        return {
            "agent": self.name,
            "decisions": decisions,
        }

    def _review_recommendation(self, recommendation: Recommendation) -> SafetyDecision:
        action = recommendation.proposed_action or {}
        entity = action.get("entity", "")
        domain = entity.split(".")[0] if "." in entity else recommendation.type

        blocked_domains = set(self.policy.get("blocked_domains", []))
        approval_required_domains = set(self.policy.get("approval_required_domains", []))
        comfort_min = self.policy.get("comfort_temperature_min", 18)
        comfort_max = self.policy.get("comfort_temperature_max", 23)

        if domain in blocked_domains:
            return SafetyDecision(
                recommendation_id=recommendation.id,
                decision="blocked",
                reason=f"Domain '{domain}' is blocked by policy.",
                required_user_confirmation="Manual override required in policy review process.",
                safer_alternative="Use passive notification instead of direct control.",
            )

        if domain == "climate":
            scheduled_temp = action.get("temperature") or action.get("target_temperature")
            if scheduled_temp is not None and (scheduled_temp < comfort_min or scheduled_temp > comfort_max):
                return SafetyDecision(
                    recommendation_id=recommendation.id,
                    decision="blocked",
                    reason="Climate target is outside comfort range.",
                    required_user_confirmation="Explicit occupant override required.",
                    safer_alternative=f"Stay within {comfort_min}-{comfort_max} C.",
                )

        if recommendation.requires_approval or domain in approval_required_domains:
            return SafetyDecision(
                recommendation_id=recommendation.id,
                decision="needs_approval",
                reason="Recommendation changes automation or comfort behavior and requires confirmation.",
                required_user_confirmation="Approve in Home Assistant or demo control panel before applying.",
                safer_alternative="Run as a staged suggestion only.",
            )

        return SafetyDecision(
            recommendation_id=recommendation.id,
            decision="approved",
            reason="Low-risk and reversible action.",
            required_user_confirmation=None,
            safer_alternative=None,
        )
