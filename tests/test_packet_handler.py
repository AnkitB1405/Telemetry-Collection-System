from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from server.database import TelemetryDatabase
from server.packet_handler import PacketHandler
from server.sequence_tracker import SequenceTracker
from utils.protocol import ACK, REGISTER_ACK, build_register_message, build_telemetry_message, encode_message


class PacketHandlerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "telemetry.db"
        self.database = TelemetryDatabase(self.db_path)
        self.handler = PacketHandler(self.database, SequenceTracker())

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _table_count(self, table_name: str) -> int:
        with sqlite3.connect(self.db_path) as connection:
            return connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

    def test_register_message_creates_device_and_returns_register_ack(self) -> None:
        payload = encode_message(build_register_message("node_1", "lab-node", 1710000000))

        result = self.handler.process(payload, ("192.168.1.10", 50000), 1710000001)

        self.assertTrue(result.handled)
        self.assertIsNotNone(result.reply)
        self.assertEqual(result.reply["type"], REGISTER_ACK)
        self.assertTrue(self.database.is_registered("node_1"))

        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT device_name, ip_address FROM devices WHERE client_id = ?",
                ("node_1",),
            ).fetchone()

        self.assertEqual(row, ("lab-node", "192.168.1.10"))

    def test_duplicate_telemetry_is_acked_without_duplicate_rows(self) -> None:
        register_payload = encode_message(build_register_message("node_1", "lab-node", 1710000000))
        self.handler.process(register_payload, ("127.0.0.1", 50000), 1710000001)

        telemetry_payload = encode_message(
            build_telemetry_message(
                "node_1",
                4,
                {
                    "cpu": 10.0,
                    "memory": 20.0,
                    "disk": 30.0,
                    "net_sent": 100,
                    "net_recv": 200,
                    "timestamp": 1710000002,
                },
            )
        )

        first = self.handler.process(telemetry_payload, ("127.0.0.1", 50000), 1710000003)
        second = self.handler.process(telemetry_payload, ("127.0.0.1", 50000), 1710000004)

        self.assertEqual(first.reply["type"], ACK)
        self.assertEqual(second.reply["type"], ACK)
        self.assertEqual(self._table_count("telemetry"), 1)
        self.assertEqual(self._table_count("network_stats"), 1)


if __name__ == "__main__":
    unittest.main()
