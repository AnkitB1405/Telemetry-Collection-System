"""Per-client sequence and network performance tracking."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict


@dataclass
class ClientSequenceState:
    packets_received: int = 0
    packets_lost: int = 0
    bytes_received: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0
    last_sequence: int | None = None
    last_latency: float = 0.0
    jitter: float = 0.0
    update_interval: float = 0.0


class SequenceTracker:
    """Tracks loss, throughput, latency, jitter, and update interval."""

    def __init__(self) -> None:
        self.clients: Dict[str, ClientSequenceState] = {}

    def record(self, client_id: str, sequence: int, packet_size: int, client_timestamp: int, server_time: int) -> Dict[str, float]:
        now = float(server_time)
        state = self.clients.setdefault(client_id, ClientSequenceState())

        if state.first_seen == 0.0:
            state.first_seen = now

        if state.last_seen:
            state.update_interval = max(0.0, now - state.last_seen)

        state.last_seen = now
        state.packets_received += 1
        state.bytes_received += packet_size

        if state.last_sequence is not None and sequence > state.last_sequence + 1:
            state.packets_lost += sequence - state.last_sequence - 1

        if state.last_sequence is None or sequence > state.last_sequence:
            state.last_sequence = sequence

        latency = max(0.0, now - float(client_timestamp))
        if state.last_latency:
            state.jitter = abs(latency - state.last_latency)
        state.last_latency = latency

        elapsed = max(now - state.first_seen, 1.0)
        expected = state.packets_received + state.packets_lost
        packet_loss = (state.packets_lost / expected) * 100.0 if expected else 0.0

        return {
            "packets_received": state.packets_received,
            "packets_lost": state.packets_lost,
            "packet_loss": round(packet_loss, 2),
            "throughput": round(state.packets_received / elapsed, 2),
            "data_rate": round(state.bytes_received / elapsed, 2),
            "latency": round(latency, 3),
            "jitter": round(state.jitter, 3),
            "update_interval": round(state.update_interval, 3),
        }
