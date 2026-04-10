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
│   ├── helpers.py
│   └── protocol.py
├── tests/
│   ├── test_client.py
│   ├── test_packet_handler.py
│   └── test_protocol.py
├── requirements.txt
├── WORKING_STEPS.md
├── PROGRAM_EXPLANATION.md
└── README.md
```

## Features

- Real Linux telemetry collection with `psutil`
- JSON-over-UDP telemetry transport
- Socket-based device registration and handshake
- Application-level UDP ACKs with bounded retries
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
python -m pip install -r requirements.txt
```

## Running the System

Start the combined server and dashboard:

```bash
python -m dashboard.app
```

Open the dashboard at `http://127.0.0.1:5000`.

Start a client:

```bash
python -m client.client --client-id node_1 --host 127.0.0.1 --port 9999 --interval 1
```

Use `127.0.0.1` only when the client and dashboard/server are running on the same machine.

For another node on your Tailscale network, use the server's Tailscale IP or MagicDNS name instead:

```bash
python -m client.client --client-id node_1 --host <server-tailscale-ip-or-name> --port 9999 --interval 1
```

Each client automatically registers over UDP before sending telemetry. The server stores the `client_id`, the client's hostname as `device_name`, and the sender IP address observed by the UDP server.

You can run multiple clients from different Linux machines by pointing them at the dashboard host.

## UDP Message Types

The client and server use explicit typed JSON messages over UDP:

- `REGISTER`: client announces itself before telemetry starts
- `REGISTER_ACK`: server confirms registration
- `TELEMETRY`: client sends one telemetry sample with a sequence number
- `ACK`: server acknowledges a telemetry sample

## Packet Format Examples

### `REGISTER`

```json
{
  "type": "REGISTER",
  "client_id": "node_1",
  "device_name": "lab-node-1",
  "timestamp": 1710000000
}
```

### `TELEMETRY`

```json
{
  "type": "TELEMETRY",
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
- Device registration now happens over UDP instead of through the dashboard.
- The client retries registration and telemetry sends up to three times if no valid ACK arrives.
- `127.0.0.1` and `localhost` only work for same-machine testing. Use a Tailscale IP or MagicDNS name for a remote server.
- Packet loss is inferred from sequence gaps per client.
- `network_stats` stores a new snapshot on each received packet so charts can show historical trends.
- The dashboard "Start Fresh" button clears stored telemetry and network history while keeping registered devices.

## Troubleshooting

- If the client times out waiting for `REGISTER_ACK`, check that:
  - the dashboard/server is running
  - the host/IP is correct
  - UDP port `9999` is reachable
  - you are not using `127.0.0.1` for a server running on another machine
