"""UDP telemetry client that sends psutil metrics every second."""

from __future__ import annotations

import argparse
import json
import logging
import socket
import time
from dataclasses import replace
from typing import Any, Dict

from client.config import DEFAULT_CLIENT_CONFIG, ClientConfig
from client.metrics import collect_metrics
from utils.helpers import configure_logging


class TelemetryClient:
    """Continuously sends telemetry to the central UDP server."""

    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self.sequence = 0
        self.logger = logging.getLogger("telemetry.client")
        collect_metrics()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.config.socket_timeout)

    def build_packet(self) -> Dict[str, Any]:
        packet = {"client_id": self.config.client_id, "sequence": self.sequence}
        packet.update(collect_metrics())
        return packet

    def send_forever(self) -> None:
        self.logger.info(
            "sending telemetry from %s to %s:%s every %.1fs",
            self.config.client_id,
            self.config.server_host,
            self.config.server_port,
            self.config.send_interval,
        )
        try:
            while True:
                payload = json.dumps(self.build_packet()).encode("utf-8")
                self.socket.sendto(payload, (self.config.server_host, self.config.server_port))
                self.sequence += 1
                time.sleep(self.config.send_interval)
        except KeyboardInterrupt:
            self.logger.info("client stopped by user")
        finally:
            self.socket.close()


def parse_args() -> ClientConfig:
    parser = argparse.ArgumentParser(description="Run a telemetry UDP client.")
    parser.add_argument("--client-id", default=DEFAULT_CLIENT_CONFIG.client_id)
    parser.add_argument("--host", default=DEFAULT_CLIENT_CONFIG.server_host)
    parser.add_argument("--port", type=int, default=DEFAULT_CLIENT_CONFIG.server_port)
    parser.add_argument("--interval", type=float, default=DEFAULT_CLIENT_CONFIG.send_interval)
    args = parser.parse_args()
    return replace(
        DEFAULT_CLIENT_CONFIG,
        client_id=args.client_id,
        server_host=args.host,
        server_port=args.port,
        send_interval=args.interval,
    )


if __name__ == "__main__":
    configure_logging()
    TelemetryClient(parse_args()).send_forever()
