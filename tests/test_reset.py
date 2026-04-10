from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from server.database import TelemetryDatabase
from server.sequence_tracker import SequenceTracker


class ResetBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "telemetry.db"
        self.database = TelemetryDatabase(self.db_path)
        self.tracker = SequenceTracker()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _table_count(self, table_name: str) -> int:
        with sqlite3.connect(self.db_path) as connection:
            return connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

    def test_clear_runtime_data_removes_history_but_keeps_devices(self) -> None:
        self.database.register_device("node_1", "lab-node", "100.64.0.5")
        self.database.insert_telemetry(
            {
                "client_id": "node_1",
                "sequence": 1,
                "cpu": 10.0,
                "memory": 20.0,
                "disk": 30.0,
                "net_sent": 100,
                "net_recv": 200,
                "timestamp": 1710000000,
            },
            server_time=1710000001,
        )
        self.database.insert_network_stats(
            "node_1",
            {
                "packets_received": 1,
                "packets_lost": 0,
                "packet_loss": 0.0,
                "throughput": 1.0,
                "data_rate": 128.0,
                "latency": 0.1,
                "jitter": 0.0,
            },
            last_updated=1710000001,
        )

        self.database.clear_runtime_data()

        self.assertEqual(self._table_count("devices"), 1)
        self.assertEqual(self._table_count("telemetry"), 0)
        self.assertEqual(self._table_count("network_stats"), 0)

    def test_sequence_tracker_reset_clears_client_state(self) -> None:
        self.tracker.record("node_1", sequence=1, packet_size=128, client_timestamp=1710000000, server_time=1710000001)

        self.tracker.reset()

        self.assertEqual(self.tracker.clients, {})


if __name__ == "__main__":
    unittest.main()
