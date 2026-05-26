from __future__ import annotations

from typing import Any, Dict, List

from src.agents.automation_agent import AutomationAgent
from src.agents.climate_agent import ClimateAgent
from src.agents.daily_life_agent import DailyLifePatternAgent
from src.agents.dashboard_agent import DashboardBuilderAgent
from src.agents.energy_agent import EnergyAgent
from src.agents.evaluation_agent import EvaluationAgent
from src.agents.safety_agent import SafetyAgent
from src.models.actions import FinalAction, FinalActionPlan
from src.models.recommendations import Recommendation
from src.models.serialization import model_to_dict


class HomeIntelligenceOrchestrator:
    def __init__(self, safety_agent: SafetyAgent) -> None:
        self.daily_life_agent = DailyLifePatternAgent()
        self.automation_agent = AutomationAgent()
        self.climate_agent = ClimateAgent()
        self.energy_agent = EnergyAgent()
        self.dashboard_agent = DashboardBuilderAgent()
        self.safety_agent = safety_agent
        self.evaluation_agent = EvaluationAgent()

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        daily_life = self.daily_life_agent.run(context)
        automation = self.automation_agent.run(context)
        climate = self.climate_agent.run(context)
        energy = self.energy_agent.run(context)
        dashboard = self.dashboard_agent.run(context)

        recommendations: List[Recommendation] = []
        recommendations.extend(automation.get("recommendations", []))
        recommendations.extend(climate.get("recommendations", []))
        recommendations.extend(energy.get("recommendations", []))
        recommendations.extend(dashboard.get("recommendations", []))

        safety_result = self.safety_agent.run({"recommendations": recommendations})
        safety_decisions = safety_result.get("decisions", [])

        evaluation_result = self.evaluation_agent.run(
            {
                "recommendations": recommendations,
                "safety_decisions": safety_decisions,
            }
        )

        final_actions = FinalActionPlan(
            actions=[
                FinalAction(
                    recommendation_id=decision.recommendation_id,
                    decision=decision.decision,
                    staged=True,
                )
                for decision in safety_decisions
            ]
        )

        return {
            "goal": context.get("goal"),
            "agents_called": [
                self.daily_life_agent.name,
                self.automation_agent.name,
                self.climate_agent.name,
                self.energy_agent.name,
                self.dashboard_agent.name,
                self.safety_agent.name,
                self.evaluation_agent.name,
            ],
            "evidence_used": context.get("daily_summary", {}),
            "event_hub_ingestion_summary": context.get("event_hub_ingestion_summary", {}),
            "daily_life_summary": daily_life,
            "recommendations": [model_to_dict(rec) for rec in recommendations],
            "safety_review": [model_to_dict(decision) for decision in safety_decisions],
            "evaluation_scores": [model_to_dict(score) for score in evaluation_result.get("scores", [])],
            "final_actions": [model_to_dict(action) for action in final_actions.actions],
            "generated_dashboard_yaml": dashboard.get("dashboard_yaml"),
        }
