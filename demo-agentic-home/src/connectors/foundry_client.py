from __future__ import annotations

from typing import Any, Dict


class FoundryClient:
    """Placeholder client for Microsoft Foundry integration.

    TODO: Replace deterministic local execution with Foundry Agent Service calls.
    """

    def run_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "agent_name": agent_name,
            "mode": "local_deterministic",
            "result": context,
        }

    def evaluate_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "recommendation_id": recommendation.get("id", "unknown"),
            "mode": "local_deterministic",
            "status": "evaluated",
        }
