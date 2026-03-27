"""Configuration for the telemetry server and dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = ROOT_DIR / "database" / "telemetry.db"


@dataclass(slots=True)
class ServerConfig:
    udp_host: str = "0.0.0.0"
    udp_port: int = 9999
    packet_size: int = 65535
    socket_timeout: float = 1.0
    offline_after_seconds: int = 10
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 5000
    history_limit: int = 120
    database_path: Path = DATABASE_PATH


DEFAULT_SERVER_CONFIG = ServerConfig()
