from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class AgentOutput:
    name: str
    summary: str
    details: Dict[str, Any]


def _match_entities(states: List[Dict[str, Any]], keys: List[str]) -> List[Dict[str, Any]]:
    lowered = [k.lower() for k in keys]
    matches: List[Dict[str, Any]] = []
    for state in states:
        entity_id = str(state.get("entity_id", "")).lower()
        if any(key in entity_id for key in lowered):
            matches.append(state)
    return matches


def dashboard_agent(states: List[Dict[str, Any]]) -> AgentOutput:
    motion = _match_entities(states, ["motion"])
    temp = _match_entities(states, ["temp", "temperature"])
    power = _match_entities(states, ["power", "energy"])
    summary = (
        f"Dashboard built from {len(states)} entities. "
        f"Detected {len(motion)} motion, {len(temp)} temperature, and {len(power)} power/energy sensors."
    )
    return AgentOutput(
        name="Dashboard Agent",
        summary=summary,
        details={
            "motion_count": len(motion),
            "temperature_count": len(temp),
            "power_count": len(power),
        },
    )


def life_pattern_agent(states: List[Dict[str, Any]]) -> AgentOutput:
    motion = _match_entities(states, ["motion"])
    occupancy_like = [s for s in motion if str(s.get("state", "")).lower() in {"on", "detected"}]
    activity = "high" if len(occupancy_like) >= 3 else "normal"
    summary = f"Daily life signal is {activity}. Active motion entities: {len(occupancy_like)}."
    return AgentOutput(
        name="Life Pattern Agent",
        summary=summary,
        details={"activity_level": activity, "active_motion_entities": len(occupancy_like)},
    )


def climate_energy_agent(states: List[Dict[str, Any]]) -> AgentOutput:
    temp_sensors = _match_entities(states, ["temp", "temperature"])
    power_sensors = _match_entities(states, ["power", "energy"])

    high_temp = 0
    for sensor in temp_sensors:
        try:
            if float(sensor.get("state")) >= 24.0:
                high_temp += 1
        except Exception:
            continue

    high_power = 0
    for sensor in power_sensors:
        try:
            if float(sensor.get("state")) >= 1000:
                high_power += 1
        except Exception:
            continue

    summary = (
        f"Climate-energy scan found {high_temp} warm zones and {high_power} high power entities."
    )
    return AgentOutput(
        name="Climate and Energy Agent",
        summary=summary,
        details={"high_temp_count": high_temp, "high_power_count": high_power},
    )


def safety_agent(states: List[Dict[str, Any]]) -> AgentOutput:
    doors = _match_entities(states, ["door", "window"])
    open_count = 0
    for door in doors:
        if str(door.get("state", "")).lower() in {"on", "open"}:
            open_count += 1

    risk = "high" if open_count >= 2 else "low"
    summary = f"Safety scan found {open_count} open door/window entities. Risk level: {risk}."
    return AgentOutput(
        name="Safety Agent",
        summary=summary,
        details={"open_entries": open_count, "risk_level": risk},
    )


def recommendation_agent(outputs: List[AgentOutput]) -> AgentOutput:
    details = {out.name: out.details for out in outputs}

    recommendations: List[Dict[str, str]] = []

    climate = details.get("Climate and Energy Agent", {})
    safety = details.get("Safety Agent", {})
    life = details.get("Life Pattern Agent", {})

    if climate.get("high_power_count", 0) > 0:
        recommendations.append(
            {
                "title": "Schedule heavy loads during low-tariff windows",
                "action_type": "optimization",
                "risk_level": "medium",
                "factory_equivalent": "Shift high-energy machine cycles to off-peak production windows",
            }
        )

    if climate.get("high_temp_count", 0) > 0:
        recommendations.append(
            {
                "title": "Reduce target temperature by 1C when rooms are inactive",
                "action_type": "automation",
                "risk_level": "low",
                "factory_equivalent": "Tune HVAC setpoints in idle production zones to cut energy use",
            }
        )

    if safety.get("risk_level") == "high":
        recommendations.append(
            {
                "title": "Enforce lock and alarm check before night mode",
                "action_type": "safety",
                "risk_level": "high",
                "factory_equivalent": "Enforce machine and perimeter safety checklist before unattended operation",
            }
        )

    if life.get("activity_level") == "high":
        recommendations.append(
            {
                "title": "Delay noisy automations until low-activity period",
                "action_type": "experience",
                "risk_level": "low",
                "factory_equivalent": "Delay non-critical maintenance actions during peak production activity",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "title": "No urgent actions. Keep monitoring baseline behavior",
                "action_type": "monitor",
                "risk_level": "low",
                "factory_equivalent": "No urgent intervention. Continue condition monitoring",
            }
        )

    summary = f"Generated {len(recommendations)} recommendation(s) with safety and optimization focus."
    return AgentOutput(
        name="Recommendation Agent",
        summary=summary,
        details={"recommendations": recommendations},
    )


def run_multi_agent_pipeline(states: List[Dict[str, Any]]) -> List[AgentOutput]:
    dash = dashboard_agent(states)
    life = life_pattern_agent(states)
    climate = climate_energy_agent(states)
    safety = safety_agent(states)
    rec = recommendation_agent([dash, life, climate, safety])
    return [dash, life, climate, safety, rec]
