"""Packet decoding, validation, and persistence workflow."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from server.database import TelemetryDatabase
from server.sequence_tracker import SequenceTracker

REQUIRED_FIELDS = {
    "client_id": str,
    "sequence": int,
    "cpu": (int, float),
    "memory": (int, float),
    "disk": (int, float),
    "net_sent": int,
    "net_recv": int,
    "timestamp": int,
}


class PacketValidationError(ValueError):
    """Raised when a UDP telemetry packet is malformed."""


def decode_packet(raw_data: bytes) -> Dict[str, Any]:
    try:
        packet = json.loads(raw_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PacketValidationError(f"invalid JSON payload: {exc}") from exc
    validate_packet(packet)
    return packet


def validate_packet(packet: Dict[str, Any]) -> None:
    if not isinstance(packet, dict):
        raise PacketValidationError("packet must decode to an object")

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in packet:
            raise PacketValidationError(f"missing required field '{field}'")
        if not isinstance(packet[field], expected_type):
            raise PacketValidationError(f"field '{field}' has invalid type")

    for metric_name in ("cpu", "memory", "disk"):
        if not 0 <= float(packet[metric_name]) <= 100:
            raise PacketValidationError(f"field '{metric_name}' must be between 0 and 100")

    if packet["sequence"] < 0:
        raise PacketValidationError("sequence must be non-negative")
    if packet["net_sent"] < 0 or packet["net_recv"] < 0:
        raise PacketValidationError("network counters must be non-negative")


class PacketHandler:
    """Processes validated telemetry packets."""

    def __init__(self, database: TelemetryDatabase, tracker: SequenceTracker) -> None:
        self.database = database
        self.tracker = tracker
        self.logger = logging.getLogger("telemetry.packet_handler")

    def process(self, raw_data: bytes, address: tuple[str, int], server_time: int) -> bool:
        packet = decode_packet(raw_data)
        client_id = packet["client_id"]

        if not self.database.is_registered(client_id):
            self.logger.warning("ignored packet from unregistered client_id=%s ip=%s", client_id, address[0])
            return False

        self.database.insert_telemetry(packet, server_time)
        stats = self.tracker.record(
            client_id=client_id,
            sequence=packet["sequence"],
            packet_size=len(raw_data),
            client_timestamp=packet["timestamp"],
            server_time=server_time,
        )
        self.database.insert_network_stats(client_id, stats, server_time)
        return True
