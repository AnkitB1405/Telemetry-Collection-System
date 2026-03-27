# Telemetry System Demo Steps

This document explains how to run and demonstrate the current version of the Distributed Telemetry Collection and Monitoring System.

## 1. Project Goal

This project demonstrates:

- UDP socket programming
- Multiple Linux telemetry clients sending real system metrics
- A central threaded UDP receiver
- Manual device registration through a Flask dashboard
- SQLite-based telemetry and network statistics storage
- Packet loss detection using sequence numbers
- Network monitoring using throughput, data rate, latency, jitter, and update rate
- A web dashboard with charts for devices and network behavior

## 2. Project Folder

Project folder:

```text
telemetry-system/
```

Main runtime folders inside the project:

- `client/` for Linux telemetry clients
- `server/` for UDP ingestion, validation, tracking, and database logic
- `dashboard/` for the Flask app, HTML templates, CSS, and Chart.js code
- `database/` for the SQLite database file
- `utils/` for shared helper functions

## 3. Before Running

Open a terminal and move to the project folder:

```bash
cd /home/shadow_e15/College/CN/telemetry-system
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

The current dependencies are:

- `Flask`
- `psutil`

## 4. Step-by-Step Execution

## Step 1: Start the Combined Server and Dashboard

Run:

```bash
python -m dashboard.app
```

What happens:

- The Flask web dashboard starts on port `5000`
- The UDP telemetry receiver starts in the same Python process
- The SQLite database is initialized automatically if it does not already exist
- The server begins listening for telemetry packets on UDP port `9999`

Expected use:

- Open `http://127.0.0.1:5000` in the browser

Important point:

- In this version, the UDP server and dashboard are not separate programs
- Starting the dashboard also starts the telemetry receiver

## Step 2: Register Devices from the Dashboard

Open the browser and go to:

```text
http://127.0.0.1:5000/devices/add
```

Enter:

- `client_id`
- `device_name`
- `ip_address`

Example:

- `client_id`: `node_1`
- `device_name`: `Lab Node 1`
- `ip_address`: `127.0.0.1`

Why this step matters:

- The server only accepts telemetry from registered `client_id` values
- Unregistered clients are ignored by the packet handler

## Step 3: Start the First Telemetry Client

Open a second terminal and run:

```bash
cd /home/shadow_e15/College/CN/telemetry-system
source .venv/bin/activate
python -m client.client --client-id node_1 --host 127.0.0.1 --port 9999 --interval 1
```

What happens:

- The client uses `psutil` to collect real system values
- It reads CPU usage
- It reads memory usage
- It reads disk usage
- It reads total network bytes sent and received
- It creates a JSON packet with a sequence number and timestamp
- It sends one UDP packet every second

## Step 4: Start More Clients

To demonstrate distributed behavior, register more devices first in the dashboard and then start more clients in separate terminals.

Example:

```bash
python -m client.client --client-id node_2 --host 127.0.0.1 --port 9999 --interval 1
python -m client.client --client-id node_3 --host 127.0.0.1 --port 9999 --interval 1
```

Why this is important:

- It shows that multiple clients can send telemetry to one UDP server
- The backend tracks each client independently
- The dashboard aggregates overall behavior across all registered devices

## Step 5: Observe the Dashboard Home Page

Visit:

```text
http://127.0.0.1:5000/
```

This page shows:

- Total active devices
- Average CPU usage across active clients
- Average memory usage
- Average disk usage
- Total packets received
- Total packet loss
- System throughput
- Total network traffic

How to explain it:

- The server stores each valid packet in SQLite
- The dashboard reads the latest telemetry and latest network statistics per device
- It computes current system-wide summary values

## Step 6: Observe the Devices Page

Visit:

```text
http://127.0.0.1:5000/devices
```

This page shows a table with:

- Device name
- Client ID
- IP address
- Status
- Last seen
- Packet loss
- Throughput

Important point:

- If a client stops sending data for more than 10 seconds, the dashboard marks it as `offline`

## Step 7: Open Device Detail Page

Click on any device from the Devices page or open:

```text
http://127.0.0.1:5000/devices/node_1
```

This page shows charts for:

- CPU usage over time
- Memory usage over time
- Disk usage over time
- Network sent and received over time
- Packet loss over time
- Throughput over time
- Latency over time
- Jitter over time

How to explain it:

- Raw device samples come from the `telemetry` table
- Derived network values come from the `network_stats` table
- Chart.js fetches data from the Flask REST API and renders it in the browser

## Step 8: Open Network Analysis Page

Visit:

```text
http://127.0.0.1:5000/network
```

This page shows system-wide network behavior:

- Packet loss graph
- Throughput graph
- Data rate graph
- Latency graph
- Jitter graph
- Update rate graph

This is useful for showing:

- How the network behaves across all clients together
- How transport metrics change over time

## 5. How the Working Can Be Explained During Demo

Use this flow while presenting:

### A. Client Side

Each Linux client repeatedly:

1. Collects real system telemetry using `psutil`
2. Adds its `client_id`
3. Adds an incrementing `sequence`
4. Adds the current Unix timestamp
5. Converts the packet into JSON
6. Sends it to the central server using UDP

### B. Server Side

For every received packet, the backend:

1. Receives the UDP packet
2. Decodes the JSON payload
3. Validates required fields and value ranges
4. Checks whether the `client_id` is registered
5. Stores the raw telemetry in SQLite
6. Compares the new sequence number with the previous one
7. Detects missing sequence values as packet loss
8. Calculates throughput, data rate, latency, jitter, and update interval
9. Stores the computed network statistics in SQLite
10. Makes the data available to the dashboard and API

### C. Dashboard Side

The Flask dashboard:

1. Reads aggregated values from SQLite
2. Shows current device states
3. Marks devices offline if no packet is received for 10 seconds
4. Exposes REST endpoints for summary and history data
5. Uses Chart.js in the browser to visualize trends over time

## 6. How Packet Loss Detection Works

Example:

- Previous packet from `node_1` had sequence `100`
- Current packet from `node_1` has sequence `104`

This means:

- Packets `101`, `102`, and `103` were not received
- Lost packets = `3`

The backend stores the last sequence number for each client and detects gaps whenever the sequence jumps.

## 7. How Performance Metrics Are Calculated

### Packet Loss Percentage

```text
Packet Loss % = Packets Lost / (Packets Received + Packets Lost) * 100
```

### Throughput

```text
Throughput = Packets Received / Elapsed Time
```

Unit:

- packets per second

### Data Rate

```text
Data Rate = Total Bytes Received / Elapsed Time
```

Unit:

- bytes per second

### Latency

```text
Latency = Server Time - Client Timestamp
```

### Jitter

Jitter is computed as the variation between the current latency and the previous latency for the same client.

### Update Rate

The dashboard derives update rate from the time gap between successive stored updates.

## 8. Database Usage

The SQLite database file is:

```text
database/telemetry.db
```

The main tables are:

- `devices`
- `telemetry`
- `network_stats`

What each table stores:

- `devices`: registered clients and their identity
- `telemetry`: raw incoming telemetry packets
- `network_stats`: computed network performance values over time

## 9. How to Stop the System

Press `Ctrl + C` in each client terminal.

Then press `Ctrl + C` in the dashboard terminal.

The UDP listener and Flask app stop together because they run in the same process.

## 10. Good Points to Mention in Viva or Presentation

- UDP is connectionless and lightweight
- UDP does not guarantee delivery, ordering, or retransmission
- Sequence tracking is used to infer packet loss
- The client sends real machine metrics rather than simulated values
- Device registration improves safety by allowing only known clients
- SQLite gives persistent storage for telemetry history
- Flask and Chart.js make the system easy to demonstrate visually
- The design is modular because client, server, database, and dashboard logic are separated into different files

## 11. Useful Demo Variations

### Faster client sending interval

```bash
python -m client.client --client-id node_1 --host 127.0.0.1 --port 9999 --interval 0.5
```

### Remote server demo

```bash
python -m client.client --client-id node_1 --host 192.168.1.20 --port 9999 --interval 1
```

### Offline detection demo

1. Start the dashboard
2. Register and run a client
3. Open the Devices page
4. Stop the client with `Ctrl + C`
5. Wait about 10 seconds
6. Show that the device status changes from `online` to `offline`

## 12. Summary

This project now demonstrates a complete telemetry monitoring workflow:

- Linux clients collect and send real telemetry data
- A threaded UDP backend receives and validates JSON packets
- The backend stores raw and computed metrics in SQLite
- Packet loss and network behavior are tracked per device
- A Flask dashboard presents both system-wide and per-device monitoring views
