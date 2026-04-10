# Telemetry System Program Explanation

This file explains the current programs and modules in the telemetry project.

Project folder:

```text
telemetry-system/
```

## 1. Project Purpose

This project is a UDP-based telemetry monitoring system for Linux nodes.

It demonstrates:

- socket programming with UDP
- client registration through a socket handshake
- application-level acknowledgements on top of UDP
- telemetry collection using real machine metrics
- packet loss detection using sequence numbers
- SQLite storage for raw and derived data
- a Flask dashboard for visualization

---

## 2. Current Folder Structure

```text
telemetry-system/
├── client/
│   ├── client.py
│   ├── config.py
│   └── metrics.py
├── server/
│   ├── aggregator.py
│   ├── config.py
│   ├── database.py
│   ├── packet_handler.py
│   ├── sequence_tracker.py
│   └── udp_server.py
├── dashboard/
│   ├── app.py
│   ├── templates/
│   └── static/
├── utils/
│   ├── helpers.py
│   └── protocol.py
├── database/
│   └── telemetry.db
├── requirements.txt
└── README.md
```

---

## 3. `client/client.py`

Purpose:

- Runs one telemetry client.

What it does:

- Creates a UDP socket.
- Uses the CLI `client_id`.
- Reads the local hostname and uses it as `device_name`.
- Sends a `REGISTER` message to the server when it starts.
- Waits for a `REGISTER_ACK`.
- Collects real metrics from the local machine.
- Builds `TELEMETRY` packets with a sequence number.
- Sends telemetry over UDP.
- Waits for an `ACK` for each telemetry packet.
- Retries registration and telemetry packets up to three times if no valid response arrives.

Important parts:

- `TelemetryClient` manages the full client workflow.
- `register_with_server()` performs UDP registration.
- `send_packet_with_ack()` handles telemetry retries.
- `send_forever()` runs the continuous loop.
- `parse_args()` reads `client_id`, host, port, and interval.

---

## 4. `client/metrics.py`

Purpose:

- Collects real system telemetry from the Linux host.

What it does:

- Reads CPU usage using `psutil`.
- Reads memory usage using `psutil`.
- Reads disk usage using `psutil`.
- Reads total network bytes sent and received.
- Adds the current Unix timestamp.

Why it is useful:

- The project uses real machine data instead of fake values.

---

## 5. `client/config.py`

Purpose:

- Stores client defaults in one place.

What it contains:

- default `client_id`
- default server host
- default server port
- default send interval
- default socket timeout

Why it is useful:

- Client behavior can be adjusted without changing the main client logic.

---

## 6. `utils/protocol.py`

Purpose:

- Defines the shared UDP message protocol used by both client and server.

What it does:

- Defines the valid message types:
  - `REGISTER`
  - `REGISTER_ACK`
  - `TELEMETRY`
  - `ACK`
- Builds protocol messages as Python dictionaries.
- Encodes messages to JSON bytes before sending.
- Decodes JSON bytes back into Python dictionaries after receiving.
- Validates fields, types, and metric ranges.

Why it is useful:

- The protocol rules are kept in one shared module.
- Client and server both follow the same message contract.

---

## 7. `server/udp_server.py`

Purpose:

- Runs the central UDP receiver.

What it does:

- Creates a UDP socket.
- Binds to the configured host and port.
- Listens continuously for incoming datagrams.
- Starts a worker thread for each received packet.
- Passes received data to the packet handler.
- Sends `REGISTER_ACK` or `ACK` responses back to the client when needed.

Why it is useful:

- It isolates low-level UDP socket handling from higher-level processing logic.

---

## 8. `server/packet_handler.py`

Purpose:

- Handles incoming protocol messages after they arrive at the UDP server.

What it does:

- Decodes and validates incoming JSON messages using `utils/protocol.py`.
- Checks the message `type`.
- For `REGISTER`:
  - stores or updates the device in the database
  - uses the client hostname from the message as `device_name`
  - uses the sender IP from the UDP socket address as `ip_address`
  - returns a `REGISTER_ACK`
- For `TELEMETRY`:
  - verifies that the client is already registered
  - stores the telemetry if the sequence number is new
  - ignores duplicate retries safely
  - updates network statistics only for new telemetry
  - returns an `ACK`

Why it is useful:

- It is the protocol-aware decision layer between raw UDP packets and the database/statistics layers.

---

## 9. `server/sequence_tracker.py`

Purpose:

- Tracks per-client sequence and network performance data.

What it does:

- Stores the last sequence seen for each client.
- Detects missing sequence numbers as packet loss.
- Tracks packets received and packets lost.
- Tracks bytes received.
- Calculates:
  - packet loss percentage
  - throughput
  - data rate
  - latency
  - jitter
  - update interval

Why it is useful:

- It keeps packet tracking and performance calculations separate from socket code.

---

## 10. `server/database.py`

Purpose:

- Handles SQLite storage and queries.

What it does:

- Creates the database tables if they do not exist.
- Stores registered devices.
- Stores raw telemetry samples.
- Stores computed network statistics.
- Uses a unique `(client_id, sequence)` index for telemetry so duplicate retries are ignored safely.
- Provides query helpers for dashboard summary, device history, and network analysis.

Main tables:

- `devices`
- `telemetry`
- `network_stats`

Why it is useful:

- It gives persistent storage and keeps SQL logic out of the client and dashboard code.

---

## 11. `server/aggregator.py`

Purpose:

- Acts as a small facade between Flask routes and database queries.

What it does:

- Returns dashboard summary data.
- Returns the list of devices.
- Returns details for a single device.
- Returns telemetry and network history for charts.
- Returns aggregated system-wide network data.

Why it is useful:

- It keeps the Flask routes simple and readable.

---

## 12. `server/config.py`

Purpose:

- Stores server and dashboard configuration values.

What it contains:

- UDP host and port
- dashboard host and port
- packet size
- socket timeout
- offline threshold
- history limit
- database path

Why it is useful:

- Centralized configuration makes the server easier to maintain and tune.

---

## 13. `dashboard/app.py`

Purpose:

- Runs the Flask dashboard and starts the UDP server in the same process.

What it does:

- Creates the Flask application.
- Creates the database helper, sequence tracker, packet handler, UDP server, and aggregator.
- Starts the UDP server automatically.
- Exposes HTML routes for:
  - dashboard overview
  - device inventory
  - device detail page
  - network analysis page
- Exposes JSON API routes for dashboard and chart data.
- Redirects the old `/devices/add` route back to the devices page because registration is now automatic through UDP.

Why it is useful:

- It is the main entry point for the whole application.

---

## 14. `dashboard/templates/` and `dashboard/static/`

Purpose:

- Build the web interface shown in the browser.

What they do:

- `templates/` contains Jinja HTML pages.
- `static/js/` fetches telemetry and network history from Flask APIs.
- `static/css/` styles the dashboard.
- Chart.js is used for line charts and time-series visualization.

Important point:

- The dashboard is now for monitoring and visualization only.
- Devices appear automatically after the UDP registration handshake.

---

## 15. `utils/helpers.py`

Purpose:

- Provides shared helper functions.

What it does:

- Configures logging.
- Formats Unix timestamps for the dashboard templates.

---

## 16. `requirements.txt`

Purpose:

- Lists Python dependencies needed by the current project.

Current dependencies:

- `Flask`
- `psutil`

---

## 17. How the Whole Project Works Together

### Step 1: Start the dashboard

- `dashboard/app.py` starts Flask.
- It also starts the UDP server in the same Python process.
- The SQLite database is initialized automatically.

### Step 2: Start a client

- `client/client.py` creates a UDP socket.
- It sends a `REGISTER` message.
- The server replies with `REGISTER_ACK`.
- The device is now known to the system.

### Step 3: Send telemetry

- The client collects metrics using `client/metrics.py`.
- It builds a `TELEMETRY` message with a sequence number.
- The server validates and stores it.
- The server calculates network metrics.
- The server replies with an `ACK`.
- If the client does not receive the ACK, it retries the same telemetry sequence.

### Step 4: Show the results

- Flask reads data from SQLite through `server/aggregator.py`.
- The dashboard pages display summary metrics, device status, and charts.
- The browser uses Chart.js to render history over time.

---

## 18. Short One-Line Summary for Key Modules

- `client/client.py`: registers a client and sends acknowledged telemetry over UDP.
- `client/metrics.py`: reads real system metrics from the local Linux machine.
- `utils/protocol.py`: defines the typed UDP message protocol.
- `server/udp_server.py`: receives UDP packets and sends protocol responses.
- `server/packet_handler.py`: processes `REGISTER` and `TELEMETRY` messages.
- `server/sequence_tracker.py`: calculates packet loss and network performance metrics.
- `server/database.py`: stores and queries devices, telemetry, and network statistics.
- `server/aggregator.py`: prepares database data for the dashboard.
- `dashboard/app.py`: runs the Flask dashboard and embedded UDP server.
- `dashboard/templates/` and `dashboard/static/`: render the monitoring UI.
- `requirements.txt`: lists the external Python packages used by the project.
