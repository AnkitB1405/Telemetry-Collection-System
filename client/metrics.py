"""Real telemetry collection helpers for Linux clients."""

from __future__ import annotations

import time
from typing import Any, Dict

import psutil


def collect_metrics() -> Dict[str, Any]:
    """Collect a single telemetry snapshot from the local host."""
    net_io = psutil.net_io_counters()
    return {
        "cpu": round(psutil.cpu_percent(interval=None), 2),
        "memory": round(psutil.virtual_memory().percent, 2),
        "disk": round(psutil.disk_usage("/").percent, 2),
        "net_sent": int(net_io.bytes_sent),
        "net_recv": int(net_io.bytes_recv),
        "timestamp": int(time.time()),
    }
