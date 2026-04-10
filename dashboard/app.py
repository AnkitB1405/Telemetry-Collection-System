"""Flask dashboard plus embedded UDP telemetry server."""

from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template, request, url_for

from server.aggregator import Aggregator
from server.config import DEFAULT_SERVER_CONFIG, ServerConfig
from server.database import TelemetryDatabase
from server.packet_handler import PacketHandler
from server.sequence_tracker import SequenceTracker
from server.udp_server import TelemetryUDPServer
from utils.helpers import configure_logging, format_timestamp


def create_app(config: ServerConfig = DEFAULT_SERVER_CONFIG) -> Flask:
    app = Flask(__name__)
    database = TelemetryDatabase(config.database_path)
    tracker = SequenceTracker()
    packet_handler = PacketHandler(database, tracker)
    udp_server = TelemetryUDPServer(config, packet_handler)
    aggregator = Aggregator(database, config)

    app.config["server_config"] = config
    app.config["database"] = database
    app.config["aggregator"] = aggregator
    app.config["tracker"] = tracker
    app.config["udp_server"] = udp_server
    app.jinja_env.globals["format_timestamp"] = format_timestamp

    udp_server.start()

    @app.route("/")
    def dashboard_home():
        return render_template("dashboard.html", summary=aggregator.dashboard_summary())

    @app.route("/devices")
    def devices_page():
        return render_template("devices.html", devices=aggregator.devices_overview())

    @app.route("/devices/add", methods=["GET", "POST"])
    def add_device():
        return redirect(url_for("devices_page"))

    @app.route("/devices/<client_id>")
    def device_detail(client_id: str):
        device = aggregator.device_details(client_id)
        if device is None:
            return render_template("device_detail.html", device=None, client_id=client_id), 404
        return render_template("device_detail.html", device=device, client_id=client_id)

    @app.route("/network")
    def network_analysis_page():
        return render_template("network_analysis.html")

    @app.route("/api/summary")
    def api_summary():
        return jsonify(aggregator.dashboard_summary())

    @app.route("/api/devices")
    def api_devices():
        return jsonify(aggregator.devices_overview())

    @app.route("/api/devices/<client_id>")
    def api_device_details(client_id: str):
        device = aggregator.device_details(client_id)
        if device is None:
            return jsonify({"error": "device not found"}), 404
        return jsonify(device)

    @app.route("/api/devices/<client_id>/metrics")
    def api_device_metrics(client_id: str):
        history = aggregator.device_history(client_id)
        return jsonify(history)

    @app.route("/api/devices/<client_id>/rename", methods=["POST"])
    def api_rename_device(client_id: str):
        payload = request.get_json(silent=True) or {}
        device_name = str(payload.get("device_name", "")).strip()

        if not device_name:
            return jsonify({"error": "device name is required"}), 400
        if len(device_name) > 64:
            return jsonify({"error": "device name must be 64 characters or fewer"}), 400
        if not database.rename_device(client_id, device_name):
            return jsonify({"error": "device not found"}), 404

        updated_device = aggregator.device_details(client_id)
        return jsonify(updated_device)

    @app.route("/api/network-analysis")
    def api_network_analysis():
        return jsonify(aggregator.network_analysis())

    @app.route("/api/reset-data", methods=["POST"])
    def api_reset_data():
        database.clear_runtime_data()
        tracker.reset()
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    configure_logging()
    app = create_app()
    app.run(
        host=DEFAULT_SERVER_CONFIG.dashboard_host,
        port=DEFAULT_SERVER_CONFIG.dashboard_port,
        debug=False,
        use_reloader=False,
    )
