"""Aggregation helpers used by the Flask dashboard."""

from __future__ import annotations

from typing import Any, Dict, List

from server.config import ServerConfig
from server.database import TelemetryDatabase


class Aggregator:
    """Convenience facade for dashboard and API data retrieval."""

    def __init__(self, database: TelemetryDatabase, config: ServerConfig) -> None:
        self.database = database
        self.config = config

    def dashboard_summary(self) -> Dict[str, Any]:
        return self.database.fetch_dashboard_summary(self.config.offline_after_seconds)

    def devices_overview(self) -> List[Dict[str, Any]]:
        return self.database.fetch_devices_overview(self.config.offline_after_seconds)

    def device_details(self, client_id: str) -> Dict[str, Any] | None:
        return self.database.fetch_device(client_id, self.config.offline_after_seconds)

    def device_history(self, client_id: str) -> Dict[str, Any]:
        return {
            "telemetry": self.database.fetch_device_telemetry_history(client_id, self.config.history_limit),
            "network": self.database.fetch_device_network_history(client_id, self.config.history_limit),
        }

    def network_analysis(self) -> List[Dict[str, Any]]:
        return self.database.fetch_network_analysis(self.config.history_limit)
