"""Threaded UDP receiver used by the dashboard application."""

from __future__ import annotations

import logging
import socket
import threading
import time

from server.config import ServerConfig
from server.packet_handler import PacketHandler, PacketValidationError


class TelemetryUDPServer:
    """Receives packets on a background thread and forwards them to the packet handler."""

    def __init__(self, config: ServerConfig, packet_handler: PacketHandler) -> None:
        self.config = config
        self.packet_handler = packet_handler
        self.logger = logging.getLogger("telemetry.udp_server")
        self.running = False
        self.thread: threading.Thread | None = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.config.udp_host, self.config.udp_port))
        self.socket.settimeout(self.config.socket_timeout)

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._serve_forever, daemon=True, name="telemetry-udp-server")
        self.thread.start()
        self.logger.info("udp server listening on %s:%s", self.config.udp_host, self.config.udp_port)

    def stop(self) -> None:
        self.running = False
        try:
            self.socket.close()
        except OSError:
            pass

    def _serve_forever(self) -> None:
        while self.running:
            try:
                payload, address = self.socket.recvfrom(self.config.packet_size)
            except socket.timeout:
                continue
            except OSError:
                break

            threading.Thread(
                target=self._process_packet,
                args=(payload, address, int(time.time())),
                daemon=True,
            ).start()

    def _process_packet(self, payload: bytes, address: tuple[str, int], server_time: int) -> None:
        try:
            self.packet_handler.process(payload, address, server_time)
        except PacketValidationError as exc:
            self.logger.warning("invalid packet from %s:%s - %s", address[0], address[1], exc)
        except Exception:
            self.logger.exception("unexpected error while processing packet from %s:%s", address[0], address[1])
