"""SQLite persistence layer for telemetry and network statistics."""

from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class TelemetryDatabase:
    """Thread-safe database helper using short-lived SQLite connections."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT UNIQUE,
                    device_name TEXT,
                    display_name TEXT,
                    ip_address TEXT,
                    registered_at INTEGER
                );

                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT,
                    sequence INTEGER,
                    cpu REAL,
                    memory REAL,
                    disk REAL,
                    net_sent INTEGER,
                    net_recv INTEGER,
                    timestamp INTEGER,
                    server_time INTEGER
                );

                CREATE TABLE IF NOT EXISTS network_stats (
                    client_id TEXT,
                    packets_received INTEGER,
                    packets_lost INTEGER,
                    packet_loss REAL,
                    throughput REAL,
                    data_rate REAL,
                    latency REAL,
                    jitter REAL,
                    last_updated INTEGER
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_telemetry_client_sequence
                ON telemetry (client_id, sequence);
                """
            )
            existing_columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(devices)").fetchall()
            }
            if "display_name" not in existing_columns:
                connection.execute("ALTER TABLE devices ADD COLUMN display_name TEXT")

    def register_device(self, client_id: str, device_name: str, ip_address: str) -> None:
        with self.lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO devices (client_id, device_name, display_name, ip_address, registered_at)
                VALUES (?, ?, NULL, ?, ?)
                ON CONFLICT(client_id) DO UPDATE SET
                    device_name = excluded.device_name,
                    ip_address = excluded.ip_address,
                    registered_at = excluded.registered_at
                """,
                (client_id, device_name, ip_address, int(time.time())),
            )

    def rename_device(self, client_id: str, display_name: str) -> bool:
        cleaned_name = display_name.strip()
        if not cleaned_name:
            return False

        with self.lock, self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE devices
                SET display_name = ?
                WHERE client_id = ?
                """,
                (cleaned_name, client_id),
            )
            return cursor.rowcount > 0

    def is_registered(self, client_id: str) -> bool:
        with self.lock, self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM devices WHERE client_id = ? LIMIT 1",
                (client_id,),
            ).fetchone()
            return row is not None

    def insert_telemetry(self, packet: Dict[str, Any], server_time: int) -> bool:
        with self.lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO telemetry (
                    client_id, sequence, cpu, memory, disk, net_sent, net_recv, timestamp, server_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    packet["client_id"],
                    packet["sequence"],
                    packet["cpu"],
                    packet["memory"],
                    packet["disk"],
                    packet["net_sent"],
                    packet["net_recv"],
                    packet["timestamp"],
                    server_time,
                ),
            )
            return cursor.rowcount > 0

    def insert_network_stats(self, client_id: str, stats: Dict[str, Any], last_updated: int) -> None:
        with self.lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO network_stats (
                    client_id, packets_received, packets_lost, packet_loss,
                    throughput, data_rate, latency, jitter, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    client_id,
                    stats["packets_received"],
                    stats["packets_lost"],
                    stats["packet_loss"],
                    stats["throughput"],
                    stats["data_rate"],
                    stats["latency"],
                    stats["jitter"],
                    last_updated,
                ),
            )

    def clear_runtime_data(self) -> None:
        with self.lock, self._connect() as connection:
            connection.execute("DELETE FROM telemetry")
            connection.execute("DELETE FROM network_stats")

    def fetch_dashboard_summary(self, offline_after_seconds: int) -> Dict[str, Any]:
        now = int(time.time())
        with self.lock, self._connect() as connection:
            latest_telemetry = connection.execute(
                """
                SELECT t.*
                FROM telemetry t
                INNER JOIN (
                    SELECT client_id, MAX(server_time) AS max_server_time
                    FROM telemetry
                    GROUP BY client_id
                ) latest
                ON latest.client_id = t.client_id AND latest.max_server_time = t.server_time
                """
            ).fetchall()
            latest_network = connection.execute(
                """
                SELECT ns.*
                FROM network_stats ns
                INNER JOIN (
                    SELECT client_id, MAX(last_updated) AS max_last_updated
                    FROM network_stats
                    GROUP BY client_id
                ) latest
                ON latest.client_id = ns.client_id AND latest.max_last_updated = ns.last_updated
                """
            ).fetchall()

        average_cpu = sum(row["cpu"] for row in latest_telemetry) / len(latest_telemetry) if latest_telemetry else 0.0
        average_memory = sum(row["memory"] for row in latest_telemetry) / len(latest_telemetry) if latest_telemetry else 0.0
        average_disk = sum(row["disk"] for row in latest_telemetry) / len(latest_telemetry) if latest_telemetry else 0.0
        active_clients = sum(1 for row in latest_telemetry if now - int(row["server_time"]) <= offline_after_seconds)
        total_network_traffic = sum((row["net_sent"] + row["net_recv"]) for row in latest_telemetry)
        total_packets_received = sum(row["packets_received"] for row in latest_network)
        total_packets_lost = sum(row["packets_lost"] for row in latest_network)
        system_throughput = sum(row["throughput"] for row in latest_network)
        system_data_rate = sum(row["data_rate"] for row in latest_network)

        return {
            "active_clients": active_clients,
            "average_cpu": round(average_cpu, 2),
            "average_memory": round(average_memory, 2),
            "average_disk": round(average_disk, 2),
            "total_network_traffic": int(total_network_traffic),
            "total_packets_received": int(total_packets_received),
            "total_packets_lost": int(total_packets_lost),
            "system_throughput": round(system_throughput, 2),
            "system_data_rate": round(system_data_rate, 2),
        }

    def fetch_devices_overview(self, offline_after_seconds: int) -> List[Dict[str, Any]]:
        now = int(time.time())
        with self.lock, self._connect() as connection:
            devices = connection.execute(
                """
                SELECT
                    d.client_id,
                    d.device_name AS registered_name,
                    d.display_name,
                    COALESCE(NULLIF(d.display_name, ''), d.device_name) AS device_name,
                    d.ip_address,
                    t.server_time AS last_seen,
                    ns.packet_loss,
                    ns.throughput
                FROM devices d
                LEFT JOIN (
                    SELECT t1.*
                    FROM telemetry t1
                    INNER JOIN (
                        SELECT client_id, MAX(server_time) AS max_server_time
                        FROM telemetry
                        GROUP BY client_id
                    ) lt
                    ON lt.client_id = t1.client_id AND lt.max_server_time = t1.server_time
                ) t ON t.client_id = d.client_id
                LEFT JOIN (
                    SELECT ns1.*
                    FROM network_stats ns1
                    INNER JOIN (
                        SELECT client_id, MAX(last_updated) AS max_last_updated
                        FROM network_stats
                        GROUP BY client_id
                    ) lns
                    ON lns.client_id = ns1.client_id AND lns.max_last_updated = ns1.last_updated
                ) ns ON ns.client_id = d.client_id
                ORDER BY COALESCE(NULLIF(d.display_name, ''), d.device_name), d.client_id
                """
            ).fetchall()

        result = []
        for row in devices:
            last_seen = row["last_seen"]
            status = "offline"
            if last_seen is not None and now - int(last_seen) <= offline_after_seconds:
                status = "online"
            result.append(
                {
                    "client_id": row["client_id"],
                    "device_name": row["device_name"],
                    "registered_name": row["registered_name"],
                    "has_custom_name": bool(row["display_name"]),
                    "ip_address": row["ip_address"],
                    "status": status,
                    "last_seen": last_seen,
                    "packet_loss": round(row["packet_loss"] or 0.0, 2),
                    "throughput": round(row["throughput"] or 0.0, 2),
                }
            )
        return result

    def fetch_device(self, client_id: str, offline_after_seconds: int) -> Optional[Dict[str, Any]]:
        devices = [device for device in self.fetch_devices_overview(offline_after_seconds) if device["client_id"] == client_id]
        return devices[0] if devices else None

    def fetch_device_telemetry_history(self, client_id: str, limit: int) -> List[Dict[str, Any]]:
        with self.lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM (
                    SELECT *
                    FROM telemetry
                    WHERE client_id = ?
                    ORDER BY server_time DESC
                    LIMIT ?
                )
                ORDER BY server_time ASC
                """,
                (client_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def fetch_device_network_history(self, client_id: str, limit: int) -> List[Dict[str, Any]]:
        with self.lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM (
                    SELECT *
                    FROM network_stats
                    WHERE client_id = ?
                    ORDER BY last_updated DESC
                    LIMIT ?
                )
                ORDER BY last_updated ASC
                """,
                (client_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def fetch_network_analysis(self, limit: int) -> List[Dict[str, Any]]:
        with self.lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    last_updated,
                    AVG(packet_loss) AS packet_loss,
                    SUM(throughput) AS throughput,
                    SUM(data_rate) AS data_rate,
                    AVG(latency) AS latency,
                    AVG(jitter) AS jitter
                FROM (
                    SELECT *
                    FROM network_stats
                    ORDER BY last_updated DESC
                    LIMIT ?
                )
                GROUP BY last_updated
                ORDER BY last_updated ASC
                """,
                (max(limit * 10, limit),),
            ).fetchall()
        return [dict(row) for row in rows[-limit:]]
