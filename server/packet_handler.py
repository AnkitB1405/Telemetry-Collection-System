"""Packet decoding, validation, and persistence workflow."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict

from server.database import TelemetryDatabase
from server.sequence_tracker import SequenceTracker
from utils.protocol import (
    ACK,
    REGISTER,
    REGISTER_ACK,
    TELEMETRY,
    ProtocolValidationError,
    build_ack_message,
    build_register_ack_message,
    decode_message,
)

PacketValidationError = ProtocolValidationError


@dataclass(slots=True)
class PacketProcessResult:
    """Outcome of processing an inbound UDP message."""

    handled: bool
    reply: Dict[str, Any] | None = None


class PacketHandler:
    """Processes validated telemetry packets."""

    def __init__(self, database: TelemetryDatabase, tracker: SequenceTracker) -> None:
        self.database = database
        self.tracker = tracker
        self.logger = logging.getLogger("telemetry.packet_handler")

    def process(self, raw_data: bytes, address: tuple[str, int], server_time: int) -> PacketProcessResult:
        packet = decode_message(raw_data)
        message_type = packet["type"]

        if message_type == REGISTER:
            self.database.register_device(packet["client_id"], packet["device_name"], address[0])
            return PacketProcessResult(
                handled=True,
                reply=build_register_ack_message(packet["client_id"], server_time),
            )

        if message_type == TELEMETRY:
            return self._process_telemetry(packet, raw_data, address, server_time)

        if message_type in {ACK, REGISTER_ACK}:
            self.logger.warning("ignored unexpected client message type=%s from %s", message_type, address[0])
            return PacketProcessResult(handled=False)

        self.logger.warning("ignored unsupported message type=%s from %s", message_type, address[0])
        return PacketProcessResult(handled=False)

    def _process_telemetry(
        self,
        packet: Dict[str, Any],
        raw_data: bytes,
        address: tuple[str, int],
        server_time: int,
    ) -> PacketProcessResult:
        client_id = packet["client_id"]

        if not self.database.is_registered(client_id):
            self.logger.warning("ignored telemetry from unregistered client_id=%s ip=%s", client_id, address[0])
            return PacketProcessResult(handled=False)

        inserted = self.database.insert_telemetry(packet, server_time)
        if inserted:
            stats = self.tracker.record(
                client_id=client_id,
                sequence=packet["sequence"],
                packet_size=len(raw_data),
                client_timestamp=packet["timestamp"],
                server_time=server_time,
            )
            self.database.insert_network_stats(client_id, stats, server_time)
        else:
            self.logger.info("received duplicate telemetry client_id=%s sequence=%s", client_id, packet["sequence"])

        return PacketProcessResult(
            handled=True,
            reply=build_ack_message(client_id, packet["sequence"], server_time),
        )
