import os
from typing import Any, Dict, List, Tuple

import requests


class HomeAssistantClient:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )

    def health(self) -> Tuple[bool, str]:
        try:
            response = self.session.get(f"{self.base_url}/api/", timeout=10)
            if response.ok:
                return True, "Connected"
            return False, f"HTTP {response.status_code}"
        except Exception as exc:  # pragma: no cover
            return False, str(exc)

    def states(self) -> List[Dict[str, Any]]:
        response = self.session.get(f"{self.base_url}/api/states", timeout=20)
        response.raise_for_status()
        return response.json()


def load_client_from_env() -> HomeAssistantClient:
    base_url = os.getenv("HA_URL", "").strip()
    token = os.getenv("HA_TOKEN", "").strip()
    if not base_url or not token:
        raise ValueError("HA_URL and HA_TOKEN must be set in environment")
    return HomeAssistantClient(base_url=base_url, token=token)
