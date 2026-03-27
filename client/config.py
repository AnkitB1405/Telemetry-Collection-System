"""Configuration for telemetry clients."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClientConfig:
    client_id: str = "node_1"
    server_host: str = "127.0.0.1"
    server_port: int = 9999
    send_interval: float = 1.0
    socket_timeout: float = 2.0


DEFAULT_CLIENT_CONFIG = ClientConfig()
