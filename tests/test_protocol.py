from __future__ import annotations

import unittest

from utils.protocol import (
    ACK,
    REGISTER,
    TELEMETRY,
    ProtocolValidationError,
    build_ack_message,
    build_register_message,
    build_telemetry_message,
    decode_message,
    encode_message,
)


class ProtocolTests(unittest.TestCase):
    def test_register_round_trip(self) -> None:
        message = build_register_message("node_1", "lab-node", 1710000000)

        decoded = decode_message(encode_message(message))

        self.assertEqual(decoded["type"], REGISTER)
        self.assertEqual(decoded["client_id"], "node_1")
        self.assertEqual(decoded["device_name"], "lab-node")

    def test_telemetry_validation_rejects_out_of_range_metrics(self) -> None:
        message = build_telemetry_message(
            "node_1",
            1,
            {
                "cpu": 125.0,
                "memory": 50.0,
                "disk": 40.0,
                "net_sent": 10,
                "net_recv": 20,
                "timestamp": 1710000000,
            },
        )

        with self.assertRaises(ProtocolValidationError):
            encode_message(message)

    def test_ack_requires_non_negative_sequence(self) -> None:
        message = build_ack_message("node_1", -1, 1710000001)

        with self.assertRaises(ProtocolValidationError):
            encode_message(message)

    def test_missing_type_is_rejected(self) -> None:
        with self.assertRaises(ProtocolValidationError):
            decode_message(b'{"client_id":"node_1"}')

    def test_telemetry_round_trip_preserves_type(self) -> None:
        message = build_telemetry_message(
            "node_1",
            7,
            {
                "cpu": 12.5,
                "memory": 48.0,
                "disk": 71.0,
                "net_sent": 100,
                "net_recv": 200,
                "timestamp": 1710000000,
            },
        )

        decoded = decode_message(encode_message(message))

        self.assertEqual(decoded["type"], TELEMETRY)
        self.assertEqual(decoded["sequence"], 7)

    def test_ack_round_trip_preserves_type(self) -> None:
        decoded = decode_message(encode_message(build_ack_message("node_1", 7, 1710000001)))

        self.assertEqual(decoded["type"], ACK)
        self.assertEqual(decoded["sequence"], 7)


if __name__ == "__main__":
    unittest.main()
