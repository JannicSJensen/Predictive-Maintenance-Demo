from typing import Dict, List

SMART_HOME_TO_FACTORY = {
    "Home Assistant": "Operational control system",
    "Motion, climate, power sensors": "Machine and plant telemetry",
    "Azure IoT": "Industrial IoT ingestion",
    "Fabric": "Operational data estate",
    "Foundry agents": "Maintenance and operations intelligence",
    "Automations": "Workflows, actions, work orders",
    "Human approval": "Safety and governance",
}


def map_recommendation_to_factory(recommendation: Dict[str, str]) -> Dict[str, str]:
    return {
        "home_recommendation": recommendation.get("title", ""),
        "factory_equivalent": recommendation.get("factory_equivalent", ""),
        "action_type": recommendation.get("action_type", ""),
        "risk_level": recommendation.get("risk_level", "medium"),
    }


def mapping_table_rows() -> List[Dict[str, str]]:
    return [
        {"Smart home": k, "Factory / predictive maintenance": v}
        for k, v in SMART_HOME_TO_FACTORY.items()
    ]
