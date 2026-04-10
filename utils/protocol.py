"""Shared UDP protocol helpers for telemetry messages."""

from __future__ import annotations

import json
from typing import Any, Dict, Mapping

REGISTER = "REGISTER"
REGISTER_ACK = "REGISTER_ACK"
TELEMETRY = "TELEMETRY"
ACK = "ACK"
STATUS_OK = "ok"
MAX_DATAGRAM_SIZE = 65535

MESSAGE_SCHEMAS: dict[str, dict[str, type[Any] | tuple[type[Any], ...]]] = {
    REGISTER: {
        "client_id": str,
        "device_name": str,
        "timestamp": int,
    },
    REGISTER_ACK: {
        "client_id": str,
        "server_time": int,
        "status": str,
    },
    TELEMETRY: {
        "client_id": str,
        "sequence": int,
        "cpu": (int, float),
        "memory": (int, float),
        "disk": (int, float),
        "net_sent": int,
        "net_recv": int,
        "timestamp": int,
    },
    ACK: {
        "client_id": str,
        "sequence": int,
        "server_time": int,
        "status": str,
    },
}


class ProtocolValidationError(ValueError):
    """Raised when a UDP protocol message is malformed."""


def build_register_message(client_id: str, device_name: str, timestamp: int) -> Dict[str, Any]:
    return {
        "type": REGISTER,
        "client_id": client_id,
        "device_name": device_name,
        "timestamp": timestamp,
    }


def build_register_ack_message(client_id: str, server_time: int, status: str = STATUS_OK) -> Dict[str, Any]:
    return {
        "type": REGISTER_ACK,
        "client_id": client_id,
        "server_time": server_time,
        "status": status,
    }


def build_telemetry_message(client_id: str, sequence: int, metrics: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "type": TELEMETRY,
        "client_id": client_id,
        "sequence": sequence,
        "cpu": metrics["cpu"],
        "memory": metrics["memory"],
        "disk": metrics["disk"],
        "net_sent": metrics["net_sent"],
        "net_recv": metrics["net_recv"],
        "timestamp": metrics["timestamp"],
    }


def build_ack_message(client_id: str, sequence: int, server_time: int, status: str = STATUS_OK) -> Dict[str, Any]:
    return {
        "type": ACK,
        "client_id": client_id,
        "sequence": sequence,
        "server_time": server_time,
        "status": status,
    }


def encode_message(message: Mapping[str, Any]) -> bytes:
    validate_message(message)
    return json.dumps(dict(message)).encode("utf-8")


def decode_message(raw_data: bytes) -> Dict[str, Any]:
    try:
        message = json.loads(raw_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolValidationError(f"invalid JSON payload: {exc}") from exc

    validate_message(message)
    return message


def validate_message(message: Mapping[str, Any]) -> None:
    if not isinstance(message, dict):
        raise ProtocolValidationError("message must decode to an object")

    message_type = message.get("type")
    if not isinstance(message_type, str):
        raise ProtocolValidationError("message field 'type' is required")
    if message_type not in MESSAGE_SCHEMAS:
        raise ProtocolValidationError(f"unsupported message type '{message_type}'")

    for field, expected_type in MESSAGE_SCHEMAS[message_type].items():
        if field not in message:
            raise ProtocolValidationError(f"missing required field '{field}'")
        if not isinstance(message[field], expected_type):
            raise ProtocolValidationError(f"field '{field}' has invalid type")

    if message_type == TELEMETRY:
        for metric_name in ("cpu", "memory", "disk"):
            if not 0 <= float(message[metric_name]) <= 100:
                raise ProtocolValidationError(f"field '{metric_name}' must be between 0 and 100")

        if message["sequence"] < 0:
            raise ProtocolValidationError("sequence must be non-negative")
        if message["net_sent"] < 0 or message["net_recv"] < 0:
            raise ProtocolValidationError("network counters must be non-negative")

    if message_type == ACK and message["sequence"] < 0:
        raise ProtocolValidationError("ack sequence must be non-negative")
