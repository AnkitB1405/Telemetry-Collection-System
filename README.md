# Distributed Telemetry Collection and Monitoring System

This project implements a complete UDP-based telemetry collection platform in Python. Linux clients collect real system metrics with `psutil`, send them as JSON over UDP, and a central Flask application receives, validates, stores, and visualizes the data with SQLite and Chart.js.

## Project Structure

```text
telemetry-system/
├── client/
│   ├── __init__.py
│   ├── client.py
│   ├── config.py
│   └── metrics.py
├── server/
│   ├── __init__.py
│   ├── aggregator.py
│   ├── config.py
│   ├── database.py
│   ├── packet_handler.py
│   ├── sequence_tracker.py
│   └── udp_server.py
├── dashboard/
│   ├── __init__.py
│   ├── app.py
│   ├── static/
│   │   ├── css/styles.css
│   │   └── js/
│   │       ├── device_detail.js
│   │       └── network_analysis.js
│   └── templates/
│       ├── add_device.html
│       ├── base.html
│       ├── dashboard.html
│       ├── device_detail.html
│       ├── devices.html
│       └── network_analysis.html
├── database/
│   └── telemetry.db
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── requirements.txt
└── README.md
```

## Features

- Real Linux telemetry collection with `psutil`
- JSON-over-UDP telemetry transport
- Manual device registration through the dashboard
- Telemetry acceptance only for registered `client_id` values
- SQLite persistence for devices, telemetry, and network statistics
- Packet loss detection using per-client sequence tracking
- Throughput, data rate, latency, jitter, and update-rate analysis
- Offline detection after 10 seconds without telemetry
- REST API endpoints for charts and dashboard widgets
- Flask web dashboard with Chart.js visualizations
- Threaded UDP packet receiver inside the same application as the dashboard

## Installation

```bash
cd telemetry-system
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the System

Start the combined server and dashboard:

```bash
python -m dashboard.app
```

Open the dashboard at `http://127.0.0.1:5000`.

Register devices from the dashboard before starting clients. Only registered `client_id` values are accepted by the UDP server.

Start a client:

```bash
python -m client.client --client-id node_1 --host 127.0.0.1 --port 9999 --interval 1
```

You can run multiple clients from different Linux machines by pointing them at the dashboard host.

## Telemetry Packet Format

```json
{
  "client_id": "node_1",
  "sequence": 1001,
  "cpu": 45.5,
  "memory": 62.3,
  "disk": 71.2,
  "net_sent": 123456,
  "net_recv": 654321,
  "timestamp": 1710000000
}
```

## Dashboard Routes

- `/` dashboard overview
- `/devices` registered device inventory
- `/devices/add` manual registration form
- `/devices/<client_id>` device detail page with charts
- `/network` network analysis page

## REST API Endpoints

- `/api/summary`
- `/api/devices`
- `/api/devices/<client_id>`
- `/api/devices/<client_id>/metrics`
- `/api/network-analysis`

## Database Schema

The application creates these tables automatically:

- `devices(id, client_id, device_name, ip_address, registered_at)`
- `telemetry(id, client_id, sequence, cpu, memory, disk, net_sent, net_recv, timestamp, server_time)`
- `network_stats(client_id, packets_received, packets_lost, packet_loss, throughput, data_rate, latency, jitter, last_updated)`

## Notes

- `timestamp` and `server_time` are stored as Unix epoch seconds.
- Packet loss is inferred from sequence gaps per client.
- `network_stats` stores a new snapshot on each received packet so charts can show historical trends.
- Device status is computed dynamically from the latest telemetry timestamp.
