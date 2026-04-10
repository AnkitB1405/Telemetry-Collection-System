"""UDP telemetry client that sends psutil metrics every second."""

from __future__ import annotations

import argparse
import ipaddress
import logging
import socket
import time
from dataclasses import replace
from typing import Callable, Dict

from client.config import DEFAULT_CLIENT_CONFIG, ClientConfig
from client.metrics import collect_metrics
from utils.protocol import (
    ACK,
    MAX_DATAGRAM_SIZE,
    REGISTER_ACK,
    build_register_message,
    build_telemetry_message,
    decode_message,
    encode_message,
)
from utils.helpers import configure_logging

MAX_SEND_ATTEMPTS = 3


class TelemetryClient:
    """Continuously sends telemetry to the central UDP server."""

    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self.sequence = 0
        self.device_name = socket.gethostname()
        self.logger = logging.getLogger("telemetry.client")
        collect_metrics()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.config.socket_timeout)

    def build_register_packet(self) -> Dict[str, Any]:
        return build_register_message(
            client_id=self.config.client_id,
            device_name=self.device_name,
            timestamp=int(time.time()),
        )

    def build_telemetry_packet(self, sequence: int | None = None) -> Dict[str, Any]:
        return build_telemetry_message(
            client_id=self.config.client_id,
            sequence=self.sequence if sequence is None else sequence,
            metrics=collect_metrics(),
        )

    def send_forever(self) -> None:
        if self._is_loopback_target():
            self.logger.warning(
                "server host %s points to loopback. This only works when the dashboard/server runs on the same machine. "
                "For another node, use the server's Tailscale IP or MagicDNS name.",
                self.config.server_host,
            )

        self.logger.info(
            "registering %s (%s) with %s:%s",
            self.config.client_id,
            self.device_name,
            self.config.server_host,
            self.config.server_port,
        )
        if not self.register_with_server():
            self.logger.error(
                "unable to register client %s with %s:%s after %s attempts. "
                "Likely causes: wrong host/IP, dashboard/server not running, UDP port %s unreachable, or using %s for a remote server.",
                self.config.client_id,
                self.config.server_host,
                self.config.server_port,
                MAX_SEND_ATTEMPTS,
                self.config.server_port,
                self.config.server_host,
            )
            self.socket.close()
            return

        self.logger.info(
            "sending telemetry from %s to %s:%s every %.1fs",
            self.config.client_id,
            self.config.server_host,
            self.config.server_port,
            self.config.send_interval,
        )
        try:
            while True:
                packet = self.build_telemetry_packet(self.sequence)
                acknowledged = self.send_packet_with_ack(packet)
                if not acknowledged:
                    self.logger.warning("dropping telemetry sample client_id=%s sequence=%s", self.config.client_id, self.sequence)
                self.sequence += 1
                time.sleep(self.config.send_interval)
        except KeyboardInterrupt:
            self.logger.info("client stopped by user")
        finally:
            self.socket.close()

    def register_with_server(self) -> bool:
        for attempt in range(1, MAX_SEND_ATTEMPTS + 1):
            packet = self.build_register_packet()
            self._send_packet(packet)
            self.logger.info("sent REGISTER attempt %s/%s", attempt, MAX_SEND_ATTEMPTS)
            self.logger.info(
                "waiting for REGISTER_ACK from %s:%s (attempt %s/%s)",
                self.config.server_host,
                self.config.server_port,
                attempt,
                MAX_SEND_ATTEMPTS,
            )

            if self._wait_for_register_ack():
                return True

            self.logger.warning(
                "timed out waiting for REGISTER_ACK from %s:%s after %.1fs (attempt %s/%s)",
                self.config.server_host,
                self.config.server_port,
                self.config.socket_timeout,
                attempt,
                MAX_SEND_ATTEMPTS,
            )

        return False

    def send_packet_with_ack(self, packet: Dict[str, Any]) -> bool:
        for attempt in range(1, MAX_SEND_ATTEMPTS + 1):
            self._send_packet(packet)
            self.logger.info(
                "sent %s attempt %s/%s for sequence=%s",
                packet["type"],
                attempt,
                MAX_SEND_ATTEMPTS,
                packet.get("sequence"),
            )

            if self._wait_for_telemetry_ack(packet["sequence"]):
                return True

        return False

    def _send_packet(self, packet: Dict[str, Any]) -> None:
        self.socket.sendto(
            encode_message(packet),
            (self.config.server_host, self.config.server_port),
        )

    def _wait_for_register_ack(self) -> bool:
        return self._wait_for_message(
            expected_type=REGISTER_ACK,
            matcher=lambda message: message["client_id"] == self.config.client_id,
        )

    def _wait_for_telemetry_ack(self, sequence: int) -> bool:
        return self._wait_for_message(
            expected_type=ACK,
            matcher=lambda message: (
                message["client_id"] == self.config.client_id and message["sequence"] == sequence
            ),
        )

    def _wait_for_message(self, expected_type: str, matcher: Callable[[Dict[str, object]], bool]) -> bool:
        try:
            while True:
                raw_data, address = self.socket.recvfrom(MAX_DATAGRAM_SIZE)
                try:
                    message = decode_message(raw_data)
                except ValueError as exc:
                    self.logger.warning("received invalid response from %s:%s - %s", address[0], address[1], exc)
                    continue

                if message["type"] != expected_type:
                    self.logger.warning("received unexpected message type=%s while waiting for %s", message["type"], expected_type)
                    continue

                if matcher(message):
                    return True

                self.logger.warning("received mismatched %s message: %s", expected_type, message)
        except socket.timeout:
            return False

    def _is_loopback_target(self) -> bool:
        host = self.config.server_host.strip().lower()
        if host == "localhost":
            return True

        try:
            return ipaddress.ip_address(host).is_loopback
        except ValueError:
            return False


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
