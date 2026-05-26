# demo-agentic-home

Local-first demo for the talk:

**Tech talk: Agentic AI concepts, patterns and use cases**

This project demonstrates a compact, explainable agentic architecture where:
1. Home Assistant provides the environment.
2. Azure Event Hub and Fabric provide telemetry and memory.
3. Foundry provides the agentic reasoning layer.
4. Agents specialize by role.
5. Guardrails control execution.

The default implementation is deterministic and local so the demo runs without cloud credentials.

## Why this demo exists

This is not just a smart-home app. It is a relatable mini-operations environment similar to predictive maintenance:
- sensors and state changes are the telemetry stream,
- Event Hub is the ingestion backbone,
- Fabric is telemetry memory and query context,
- Foundry-style agents reason and recommend,
- safety/evaluation guardrails gate execution.

## Architecture

### Real setup path

Home Assistant event bus
-> Home Assistant Azure Event Hub integration
-> Azure Event Hub
-> Event Hub Capture / Stream Analytics / Event Hub consumer / Fabric Eventstream
-> Microsoft Fabric / OneLake / Lakehouse
-> Microsoft Foundry agents
-> Safety and evaluation guardrails
-> staged or approved Home Assistant action

### Local demo path (implemented here)

sample Home Assistant events
-> local Azure Event Hub integration simulator
-> local Event Hub envelope store
-> local Fabric-like memory connector
-> local deterministic agent workflow
-> safety/evaluation review
-> Home Assistant automation YAML and dashboard YAML output

## Project structure

```text
/demo-agentic-home
  /src
    /agents
      base.py
      orchestrator.py
      automation_agent.py
      daily_life_agent.py
      climate_agent.py
      energy_agent.py
      safety_agent.py
      dashboard_agent.py
      evaluation_agent.py
    /connectors
      home_assistant.py
      azure_event_hub.py
      fabric_memory.py
      foundry_client.py
    /models
      telemetry.py
      recommendations.py
      actions.py
      serialization.py
    /workflows
      home_intelligence_workflow.py
    /sample_data
      home_assistant_events.json
      energy_readings.json
      climate_readings.json
    /config
      safety_policy.yaml
      home_assistant_azure_event_hub_example.yaml
    /ui
      app.py
    main.py
  /data
  README.md
  requirements.txt
  .env.example
```

## Run locally

## Fastest option (demo script)

PowerShell script (creates virtual environment, installs mode-specific dependencies, and runs demo):

```bash
./run-demo.ps1
```

Run UI mode:

```bash
./run-demo.ps1 -Mode ui
```

Skip dependency install on repeat runs:

```bash
./run-demo.ps1 -SkipInstall
```

CMD wrapper (same behavior):

```bash
run-demo.cmd
```

Windows path-length note:
- The script uses a shorter default venv path: `%USERPROFILE%\\.venvs\\demo-agentic-home`.
- This avoids common `WinError 206` path-too-long issues when installing UI dependencies like Streamlit in deep project paths.
- Override venv location if needed using env var `DEMO_AGENTIC_HOME_VENV_PATH`.

## 1) Install dependencies

```bash
pip install -r requirements.txt
```

Alternative split dependency files:
- CLI only: `pip install -r requirements-cli.txt`
- UI mode: `pip install -r requirements-ui.txt`

## 2) Run CLI demo

```bash
python -m src.main
```

## 3) Optional Streamlit UI

```bash
streamlit run src/ui/app.py
```

No real Azure, Fabric, Home Assistant, or Foundry credentials are required for local mode.

## Required demo sequence implemented

The workflow executes this end-to-end sequence:
1. Loads sample Home Assistant telemetry.
2. Simulates Home Assistant event-bus events.
3. Filters selected events as Home Assistant Azure Event Hub integration would.
4. Simulates publishing selected events to Azure Event Hub.
5. Simulates consuming Event Hub events into a Fabric-like memory layer.
6. Produces an Event Hub ingestion summary.
7. Produces a home activity summary.
8. Asks orchestrator:
   - "What does daily life look like in this home, and what automations would improve comfort and energy usage?"
9. Calls specialist agents:
   - Daily Life Pattern Agent
   - Automation Agent
   - Climate Agent
   - Energy Agent
   - Dashboard Builder Agent
10. Produces structured recommendations.
11. Runs Safety Agent review on every recommendation.
12. Runs Evaluation Agent scoring.
13. Outputs:
   - Azure Event Hub ingestion summary
   - home activity summary
   - daily-life findings
   - recommended automations
   - climate recommendations
   - energy recommendations
   - generated Home Assistant automation YAML
   - generated Lovelace dashboard YAML
   - safety decisions (approved / needs_approval / blocked)
   - evaluation scores
   - architecture recap

## Home Assistant Azure Event Hub integration notes

Official integration reference:
- https://www.home-assistant.io/integrations/azure_event_hub/

In a real deployment, Home Assistant can send event-bus events to Azure Event Hub using:
- Event Hub namespace
- Event Hub instance/name
- Shared Access Policy with Send claim
- Shared Access Key or connection string
- `send_interval` (defaults to 5 seconds)
- optional filters to restrict domains/entities

Example `configuration.yaml` snippet:

```yaml
azure_event_hub:
  filter:
    include_domains:
      - binary_sensor
      - sensor
      - climate
      - light
      - switch
    include_entity_globs:
      - binary_sensor.*_motion
      - binary_sensor.*_occupancy
      - sensor.*_temperature
      - sensor.*_humidity
      - sensor.*_power*
      - sensor.*_energy*
    include_entities:
      - sensor.home_power_consumption
      - sensor.grid_energy_price
      - climate.office
      - climate.living_room
      - light.hallway
      - switch.media_center
    exclude_domains:
      - camera
      - media_player
      - alarm_control_panel
      - lock
```

**Warning:**
Do not send every Home Assistant event to Azure Event Hub in a real environment. Use filters to avoid excessive storage, bandwidth, cost, and sensitive data exposure.

## Guardrails and staging behavior

Safety policy lives in `src/config/safety_policy.yaml`.

By default:
- blocked domains include locks and alarms,
- climate/automation style changes need approval,
- out-of-range comfort changes are blocked,
- actions are staged by default and not auto-executed.

## Mapping of agents to talk concepts

- `HomeIntelligenceOrchestrator`: Coordinates goal, evidence, agents, and final output.
- `DailyLifePatternAgent`: explains occupancy routines and anomalies.
- `AutomationAgent`: proposes low-risk automations with YAML.
- `ClimateAgent`: comfort + efficiency recommendations.
- `EnergyAgent`: standby/peak/scheduling optimizations.
- `DashboardBuilderAgent`: generates Lovelace dashboard YAML.
- `SafetyAgent`: applies guardrails and decisioning.
- `EvaluationAgent`: scores recommendation quality.

## Local-to-real integration handoff points

- Home Assistant real APIs: `src/connectors/home_assistant.py`
- Azure Event Hub SDK integration: `src/connectors/azure_event_hub.py`
- Fabric/OneLake/KQL integration: `src/connectors/fabric_memory.py`
- Foundry agent service integration: `src/connectors/foundry_client.py`

Each connector includes clear TODO markers for replacement with real cloud services.

## Environment variables for future real integrations

See `.env.example`:

```env
AZURE_EVENT_HUB_CONNECTION_STRING=
AZURE_EVENT_HUB_NAME=
AZURE_EVENT_HUB_CONSUMER_GROUP=$Default
HOME_ASSISTANT_URL=
HOME_ASSISTANT_TOKEN=
FOUNDRY_PROJECT_ENDPOINT=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
```

These are optional in local demo mode.
