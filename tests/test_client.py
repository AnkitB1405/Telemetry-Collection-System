from __future__ import annotations

import socket
import unittest
from unittest.mock import patch

from client.client import TelemetryClient
from client.config import ClientConfig
from utils.protocol import (
    REGISTER,
    TELEMETRY,
    build_ack_message,
    build_register_ack_message,
    build_telemetry_message,
    encode_message,
)


class FakeSocket:
    def __init__(self, responses: list[tuple[bytes, tuple[str, int]] | Exception]) -> None:
        self.responses = list(responses)
        self.sent_packets: list[tuple[dict[str, object], tuple[str, int]]] = []
        self.timeout: float | None = None
        self.closed = False

    def settimeout(self, timeout: float) -> None:
        self.timeout = timeout

    def sendto(self, payload: bytes, address: tuple[str, int]) -> None:
        from utils.protocol import decode_message

        self.sent_packets.append((decode_message(payload), address))

    def recvfrom(self, _packet_size: int) -> tuple[bytes, tuple[str, int]]:
        if not self.responses:
            raise socket.timeout()

        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self) -> None:
        self.closed = True


class TelemetryClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ClientConfig(client_id="node_1", server_host="127.0.0.1", server_port=9999, send_interval=1.0)
        self.metrics = {
            "cpu": 12.0,
            "memory": 34.0,
            "disk": 56.0,
            "net_sent": 100,
            "net_recv": 200,
            "timestamp": 1710000000,
        }

    def _build_client(self, fake_socket: FakeSocket, config: ClientConfig | None = None) -> TelemetryClient:
        with patch("client.client.socket.socket", return_value=fake_socket), patch(
            "client.client.socket.gethostname",
            return_value="lab-node",
        ), patch("client.client.collect_metrics", return_value=self.metrics):
            return TelemetryClient(config or self.config)

    def test_register_retries_until_register_ack_arrives(self) -> None:
        fake_socket = FakeSocket(
            [
                socket.timeout(),
                (encode_message(build_register_ack_message("node_1", 1710000001)), ("127.0.0.1", 9999)),
            ]
        )
        client = self._build_client(fake_socket)

        registered = client.register_with_server()

        self.assertTrue(registered)
        self.assertEqual(len(fake_socket.sent_packets), 2)
        self.assertTrue(all(packet["type"] == REGISTER for packet, _address in fake_socket.sent_packets))

    def test_telemetry_retries_same_sequence_until_ack_arrives(self) -> None:
        fake_socket = FakeSocket(
            [
                socket.timeout(),
                (encode_message(build_ack_message("node_1", 7, 1710000001)), ("127.0.0.1", 9999)),
            ]
        )
        client = self._build_client(fake_socket)
        packet = build_telemetry_message("node_1", 7, self.metrics)

        acknowledged = client.send_packet_with_ack(packet)

        self.assertTrue(acknowledged)
        self.assertEqual(len(fake_socket.sent_packets), 2)
        self.assertTrue(all(sent["type"] == TELEMETRY for sent, _address in fake_socket.sent_packets))
        self.assertEqual([sent["sequence"] for sent, _address in fake_socket.sent_packets], [7, 7])

    def test_telemetry_returns_false_after_max_retries(self) -> None:
        fake_socket = FakeSocket([socket.timeout(), socket.timeout(), socket.timeout()])
        client = self._build_client(fake_socket)
        packet = build_telemetry_message("node_1", 9, self.metrics)

        acknowledged = client.send_packet_with_ack(packet)

        self.assertFalse(acknowledged)
        self.assertEqual(len(fake_socket.sent_packets), 3)

    def test_send_forever_warns_about_loopback_host_for_remote_use(self) -> None:
        fake_socket = FakeSocket([socket.timeout(), socket.timeout(), socket.timeout()])
        client = self._build_client(fake_socket)

        with self.assertLogs("telemetry.client", level="WARNING") as captured:
            client.send_forever()

        output = "\n".join(captured.output)
        self.assertIn("points to loopback", output)
        self.assertIn("Tailscale IP or MagicDNS name", output)

    def test_send_forever_logs_actionable_registration_failure(self) -> None:
        config = ClientConfig(client_id="node_1", server_host="100.64.0.5", server_port=9999, send_interval=1.0)
        fake_socket = FakeSocket([socket.timeout(), socket.timeout(), socket.timeout()])
        client = self._build_client(fake_socket, config=config)

        with self.assertLogs("telemetry.client", level="INFO") as captured:
            client.send_forever()

        output = "\n".join(captured.output)
        self.assertIn("waiting for REGISTER_ACK from 100.64.0.5:9999", output)
        self.assertIn("unable to register client node_1 with 100.64.0.5:9999 after 3 attempts", output)
        self.assertIn("wrong host/IP", output)
        self.assertIn("UDP port 9999 unreachable", output)


if __name__ == "__main__":
    unittest.main()
