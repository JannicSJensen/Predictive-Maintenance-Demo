# Predictive-Maintenance-Demo

A hackathon demo that uses Home Assistant as a miniature operations environment to show Agentic AI patterns.

## Storyline
- Agents are the next wave.
- An agent combines model, instructions, tools, memory, actions, and feedback.
- Agentic systems move from single assistants to coordinated multi-agent workflows.
- Microsoft Foundry and Agent Framework provide platform capabilities (tools, memory, orchestration, controls).
- Demo uses Home Assistant as a realistic operations sandbox.
- The same architecture maps directly to predictive maintenance and factory operations.

## Smart Home to Factory Mapping
| Smart home | Factory / predictive maintenance |
| --- | --- |
| Home Assistant | Operational control system |
| Motion, climate, power sensors | Machine and plant telemetry |
| Azure IoT | Industrial IoT ingestion |
| Fabric | Operational data estate |
| Foundry agents | Maintenance / operations intelligence |
| Automations | Workflows, actions, work orders |
| Human approval | Safety and governance |

## What this demo does
- Pulls entities from Home Assistant using the REST API.
- Runs a coordinated multi-agent pipeline:
  - Dashboard agent
  - Daily-life understanding agent
  - Automation recommendation agent
  - Climate and energy optimization agent
  - Safety and governance agent
- Produces actions with human approval gates.
- Displays the direct factory translation of each recommendation.

## Quick start
1. Create virtual environment and install dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure environment.

```powershell
Copy-Item .env.example .env
```

Set values in `.env`:
- `HA_URL` (example: `http://homeassistant.local:8123`)
- `HA_TOKEN` (long-lived access token)

3. Run the app.

```powershell
streamlit run src/app.py
```

4. Open the URL shown by Streamlit (usually `http://localhost:8501`).

## Home Assistant setup
- Create a long-lived access token:
  - Home Assistant -> Profile -> Long-Lived Access Tokens.
- Ensure the machine running this demo can access your Home Assistant URL.

## Suggested entities
The demo auto-discovers all states, but it works best if you have:
- Motion sensors: `binary_sensor.*motion*`
- Temperature sensors: `sensor.*temp*`
- Humidity sensors: `sensor.*humidity*`
- Power sensors: `sensor.*power*` or `sensor.*energy*`
- Presence indicators: `person.*` or occupancy binary sensors

## Notes for your talk
- Use this as a "mini operations center" where rooms = production zones and appliances = machines.
- Emphasize that recommendations are gated by human approval.
- Point out how the same agent graph can be switched from home telemetry to plant telemetry.

## Repo layout
- `src/app.py` Streamlit UI and orchestration flow
- `src/home_assistant_client.py` Home Assistant API client
- `src/agents.py` Multi-agent recommendation logic
- `src/factory_mapping.py` Home to factory translation helpers
- `.env.example` Environment template
