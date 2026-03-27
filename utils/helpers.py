"""Shared helper functions."""

from __future__ import annotations

import logging
from datetime import datetime


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def format_timestamp(timestamp: int | None) -> str:
    if not timestamp:
        return "Never"
    return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
