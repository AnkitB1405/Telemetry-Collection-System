from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from server.database import TelemetryDatabase


class DeviceRenameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "telemetry.db"
        self.database = TelemetryDatabase(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_custom_device_name_survives_future_registrations(self) -> None:
        self.database.register_device("node_1", "shadow", "127.0.0.1")

        renamed = self.database.rename_device("node_1", "Main Laptop")
        self.database.register_device("node_1", "shadow", "100.64.0.5")

        device = self.database.fetch_device("node_1", offline_after_seconds=10)

        self.assertTrue(renamed)
        self.assertIsNotNone(device)
        self.assertEqual(device["device_name"], "Main Laptop")
        self.assertEqual(device["registered_name"], "shadow")
        self.assertTrue(device["has_custom_name"])
        self.assertEqual(device["ip_address"], "100.64.0.5")

    def test_rename_device_returns_false_when_client_is_missing(self) -> None:
        renamed = self.database.rename_device("missing-node", "Demo Node")

        self.assertFalse(renamed)


if __name__ == "__main__":
    unittest.main()
