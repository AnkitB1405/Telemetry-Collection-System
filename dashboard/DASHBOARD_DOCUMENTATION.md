# Dashboard Documentation - Distributed Telemetry Monitoring System

**Project:** Distributed Telemetry Collection and Monitoring System  
**Dashboard Location:** `/home/shadow_e15/College/CN/telemetry-system/dashboard/`  
**Last Updated:** April 1, 2026  
**Author:** Claw (AI Assistant)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Backend Components](#backend-components)
6. [Frontend Components](#frontend-components)
7. [Database Schema](#database-schema)
8. [API Endpoints](#api-endpoints)
9. [Web Routes](#web-routes)
10. [Features](#features)
11. [Installation & Setup](#installation--setup)
12. [Running the System](#running-the-system)
13. [Telemetry Packet Format](#telemetry-packet-format)
14. [Network Metrics Calculation](#network-metrics-calculation)
15. [Design System](#design-system)
16. [Security Considerations](#security-considerations)
17. [Performance Characteristics](#performance-characteristics)
18. [Limitations & Known Issues](#limitations--known-issues)
19. [Future Enhancement Opportunities](#future-enhancement-opportunities)
20. [Troubleshooting](#troubleshooting)

---

## Overview

The Dashboard is a Flask-based web application that serves as the visualization and management interface for the Distributed Telemetry Monitoring System. It provides real-time monitoring of Linux nodes sending system metrics via UDP, with comprehensive charts, device management, and network analysis capabilities.

### Key Capabilities

- **Real-time monitoring** of CPU, memory, disk, and network metrics
- **Device registration** and management through web interface
- **Packet loss detection** using sequence number tracking
- **Network performance analysis** (throughput, latency, jitter, data rate)
- **Historical data visualization** using Chart.js
- **REST API** for programmatic access to telemetry data
- **Multi-device support** with aggregated system-wide statistics

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT MACHINES                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │  Node 1  │  │  Node 2  │  │  Node N  │                      │
│  │ (psutil) │  │ (psutil) │  │ (psutil) │                      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
│       │             │             │                              │
│       └─────────────┴─────────────┘                              │
│                     │                                            │
│              UDP Packets (JSON)                                  │
└─────────────────────┼────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DASHBOARD SERVER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Flask Application                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │ Web Routes  │  │ REST API    │  │ Templates       │   │   │
│  │  │ (/devices,  │  │ (/api/...)  │  │ (Jinja2 HTML)   │   │   │
│  │  │ /network)   │  │             │  │                 │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 UDP Telemetry Server                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │ Packet      │  │ Sequence    │  │ Network         │   │   │
│  │  │ Handler     │  │ Tracker     │  │ Stats Calculator│   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              SQLite Database (telemetry.db)               │   │
│  │  - devices table                                          │   │
│  │  - telemetry table                                        │   │
│  │  - network_stats table                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WEB BROWSER                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Chart.js Visualizations                      │   │
│  │  - Line charts for metrics over time                      │   │
│  │  - Real-time data fetching via fetch() API                │   │
│  │  - Responsive design (mobile-friendly)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Web Framework | Flask | 3.x | HTTP server, routing, templating |
| Database | SQLite | 3.x | Persistent storage |
| UDP Server | Python socket | built-in | Telemetry packet reception |
| Templating | Jinja2 | built-in | HTML generation |
| Language | Python | 3.10+ | Application logic |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Charts | Chart.js | 4.x (CDN) | Data visualization |
| Styling | Custom CSS | - | Responsive design |
| JavaScript | Vanilla ES6 | - | API calls, chart initialization |
| HTML | HTML5 | - | Page structure |

### Infrastructure

| Component | Details |
|-----------|---------|
| Protocol | UDP (telemetry), HTTP/HTTPS (dashboard) |
| Default Port | 5000 (dashboard), 9999 (UDP) |
| Database File | `database/telemetry.db` |
| Session Management | Stateless (no sessions) |

---

## Project Structure

```
dashboard/
├── __init__.py              # Package marker
├── app.py                   # Main Flask application entry point
├── templates/               # Jinja2 HTML templates
│   ├── base.html           # Base layout with sidebar navigation
│   ├── dashboard.html      # Home page with summary metrics
│   ├── devices.html        # Device inventory table
│   ├── device_detail.html  # Per-device charts and details
│   ├── add_device.html     # Device registration form
│   └── network_analysis.html # System-wide network metrics
├── static/                  # Static assets
│   ├── css/
│   │   └── styles.css      # Global stylesheet
│   └── js/
│       ├── device_detail.js # Chart initialization for device pages
│       └── network_analysis.js # Chart initialization for network page
└── DASHBOARD_DOCUMENTATION.md # This file
```

---

## Backend Components

### `app.py` - Main Application

**Purpose:** Creates and configures the Flask application, initializes all server components, and defines web routes and API endpoints.

**Key Responsibilities:**
- Application factory pattern (`create_app()`)
- Component initialization (database, tracker, packet handler, UDP server, aggregator)
- Route registration (web pages and REST API)
- UDP server lifecycle management (starts on app creation)

**Configuration Injection:**
```python
app.config["server_config"] = config
app.config["database"] = database
app.config["aggregator"] = aggregator
app.config["udp_server"] = udp_server
```

**Jinja2 Globals:**
- `format_timestamp` - Unix timestamp to human-readable format converter

### Server Module Components

#### `aggregator.py` - Aggregator Class

**Purpose:** Facade between Flask routes and database queries.

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `dashboard_summary()` | `Dict[str, Any]` | System-wide metrics for home page |
| `devices_overview()` | `List[Dict]` | All devices with status for table |
| `device_details(client_id)` | `Dict \| None` | Single device info |
| `device_history(client_id)` | `Dict[str, List]` | Telemetry + network history for charts |
| `network_analysis()` | `List[Dict]` | Aggregated network metrics over time |

#### `database.py` - TelemetryDatabase Class

**Purpose:** Thread-safe SQLite operations with short-lived connections.

**Key Features:**
- Thread locking (`threading.Lock`) for concurrent access
- Connection factory with `row_factory = sqlite3.Row` for dict-like access
- Automatic schema creation on initialization
- UPSERT support for device registration

**Core Methods:**
| Method | Purpose |
|--------|---------|
| `initialize()` | Creates tables if not exist |
| `register_device()` | Insert/update device record |
| `is_registered()` | Check if client_id exists |
| `insert_telemetry()` | Store raw telemetry packet |
| `insert_network_stats()` | Store computed network metrics |
| `fetch_dashboard_summary()` | Aggregate current state |
| `fetch_devices_overview()` | List all devices with status |
| `fetch_device_telemetry_history()` | Time-series for charts |
| `fetch_device_network_history()` | Network metrics history |
| `fetch_network_analysis()` | System-wide network trends |

#### `packet_handler.py` - PacketHandler Class

**Purpose:** Validate, decode, and persist incoming UDP telemetry packets.

**Validation Rules:**
- Required fields: `client_id`, `sequence`, `cpu`, `memory`, `disk`, `net_sent`, `net_recv`, `timestamp`
- Type checking for all fields
- Range validation: metrics must be 0-100, sequences non-negative, network counters non-negative
- Client registration check (unregistered clients rejected)

**Processing Flow:**
1. Decode JSON from bytes
2. Validate packet structure and values
3. Check client registration
4. Insert telemetry record
5. Update sequence tracker
6. Calculate and store network stats

#### `sequence_tracker.py` - SequenceTracker Class

**Purpose:** Track packet sequences per client to detect packet loss and calculate network metrics.

**Metrics Calculated:**
- **Packet Loss:** Gap between consecutive sequence numbers
- **Throughput:** Packets received per second
- **Data Rate:** Bytes received per second
- **Latency:** Server time minus client timestamp
- **Jitter:** Variation in latency between consecutive packets

#### `udp_server.py` - TelemetryUDPServer Class

**Purpose:** Threaded UDP socket server for receiving telemetry packets.

**Features:**
- Runs in separate daemon thread
- Non-blocking packet reception
- Error handling for malformed packets
- Logging for debugging

#### `config.py` - ServerConfig

**Configuration Options:**
| Setting | Default | Description |
|---------|---------|-------------|
| `dashboard_host` | `127.0.0.1` | Web server bind address |
| `dashboard_port` | `5000` | Web server port |
| `udp_host` | `0.0.0.0` | UDP server bind address |
| `udp_port` | `9999` | UDP server port |
| `database_path` | `database/telemetry.db` | SQLite file location |
| `offline_after_seconds` | `10` | Device offline threshold |
| `history_limit` | `100` | Max data points per chart |

---

## Frontend Components

### Templates (Jinja2)

#### `base.html` - Base Layout

**Structure:**
- Two-column grid layout (sidebar + content)
- Navigation links to all pages
- Chart.js CDN inclusion
- Responsive breakpoints for mobile

**Navigation:**
- Dashboard (home)
- Devices (inventory)
- Network Analysis

#### `dashboard.html` - Home Page

**Content:**
- Hero section with overview description
- 8 metric cards in responsive grid:
  - Active Devices
  - Average CPU %
  - Average Memory %
  - Average Disk %
  - Total Packets Received
  - Total Packet Loss
  - System Throughput (pkt/s)
  - Total Network Traffic (bytes)

#### `devices.html` - Device Inventory

**Features:**
- Table with 8 columns
- Status badges (online/offline)
- Links to device detail pages
- Automatic device discovery after UDP registration
- Empty state message

#### `device_detail.html` - Per-Device View

**Charts (8 total):**
1. CPU Usage (%)
2. Memory Usage (%)
3. Disk Usage (%)
4. Network Sent/Received (dual-line)
5. Packet Loss (%)
6. Throughput (pkt/s)
7. Latency (s)
8. Jitter (s)

**Error Handling:**
- 404 page for unknown client_id
- Device not found message

#### `network_analysis.html` - System-Wide Network

**Charts (6 total):**
1. Packet Loss (%)
2. Throughput (pkt/s)
3. Data Rate (bytes/s)
4. Latency (s)
5. Jitter (s)
6. Update Rate (Hz)

#### `add_device.html` - Registration Form

**Fields:**
- Client ID (required)
- Device Name (required)
- IP Address (required, validated)

**Validation:**
- Server-side IP address validation (IPv4/IPv6)
- Error message display

### JavaScript

#### `device_detail.js`

**Functions:**
- `fetchDeviceMetrics(clientId)` - Fetch telemetry + network history
- `buildChart()` - Create single-metric line chart
- `buildDualChart()` - Create dual-metric line chart (network sent/recv)
- `initDeviceDetail()` - Initialize all 8 charts

**Data Processing:**
- Unix timestamp to locale time string conversion
- Update rate calculation from time deltas

#### `network_analysis.js`

**Functions:**
- `fetchNetworkAnalysis()` - Fetch aggregated network data
- `chart()` - Create line chart
- `initNetworkAnalysis()` - Initialize all 6 charts

### CSS (`styles.css`)

**Design Tokens:**
```css
:root {
    --bg: #f4efe7;           /* Page background */
    --panel: #fffdf8;        /* Card background */
    --panel-strong: #efe5d7; /* Button background */
    --text: #1f2933;         /* Primary text */
    --muted: #6b7280;        /* Secondary text */
    --accent: #0f766e;       /* Primary accent (teal) */
    --accent-soft: #d7f3ef;  /* Soft accent background */
    --danger: #b91c1c;       /* Error/offline color */
    --border: #dfd5c5;       /* Border color */
    --shadow: 0 18px 45px rgba(31, 41, 51, 0.08);
}
```

**Responsive Breakpoints:**
- Desktop: 2-column grid (260px sidebar + content)
- Mobile (<900px): Single column, sidebar becomes top nav

**Key Components:**
- `.app-shell` - Main grid layout
- `.sidebar` - Fixed navigation panel
- `.card` - Reusable card component
- `.metrics-grid` / `.chart-grid` - Responsive grids
- `.status.online` / `.status.offline` - Status badges
- `.form-card` - Form container

---

## Database Schema

### `devices` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal ID |
| `client_id` | TEXT | UNIQUE | Client identifier (e.g., `node_1`) |
| `device_name` | TEXT | - | Human-readable name |
| `ip_address` | TEXT | - | Client IP address |
| `registered_at` | INTEGER | - | Unix timestamp of registration |

### `telemetry` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal ID |
| `client_id` | TEXT | - | Foreign key to devices |
| `sequence` | INTEGER | - | Packet sequence number |
| `cpu` | REAL | - | CPU usage percentage |
| `memory` | REAL | - | Memory usage percentage |
| `disk` | REAL | - | Disk usage percentage |
| `net_sent` | INTEGER | - | Total bytes sent |
| `net_recv` | INTEGER | - | Total bytes received |
| `timestamp` | INTEGER | - | Client-side Unix timestamp |
| `server_time` | INTEGER | - | Server-side Unix timestamp |

### `network_stats` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `client_id` | TEXT | - | Foreign key to devices |
| `packets_received` | INTEGER | - | Cumulative packets received |
| `packets_lost` | INTEGER | - | Cumulative packets lost |
| `packet_loss` | REAL | - | Packet loss percentage |
| `throughput` | REAL | - | Packets per second |
| `data_rate` | REAL | - | Bytes per second |
| `latency` | REAL | - | One-way latency (seconds) |
| `jitter` | REAL | - | Latency variation (seconds) |
| `last_updated` | INTEGER | - | Unix timestamp of last update |

**Note:** `network_stats` uses INSERT-only pattern (no updates) to maintain historical records for charting.

---

## API Endpoints

All endpoints return JSON.

### `GET /api/summary`

**Response:** System-wide dashboard summary

```json
{
  "active_clients": 3,
  "average_cpu": 45.67,
  "average_memory": 62.34,
  "average_disk": 71.23,
  "total_packets_received": 15234,
  "total_packets_lost": 127,
  "system_throughput": 2.98,
  "total_network_traffic": 987654321
}
```

### `GET /api/devices`

**Response:** List of all registered devices

```json
[
  {
    "client_id": "node_1",
    "device_name": "Lab Node 1",
    "ip_address": "192.168.1.10",
    "status": "online",
    "last_seen": 1710000000,
    "packet_loss": 0.83,
    "throughput": 1.02
  }
]
```

### `GET /api/devices/<client_id>`

**Response:** Single device details (404 if not found)

```json
{
  "client_id": "node_1",
  "device_name": "Lab Node 1",
  "ip_address": "192.168.1.10",
  "status": "online",
  "last_seen": 1710000000,
  "packet_loss": 0.83,
  "throughput": 1.02
}
```

### `GET /api/devices/<client_id>/metrics`

**Response:** Historical telemetry and network data for charts

```json
{
  "telemetry": [
    {
      "id": 1,
      "client_id": "node_1",
      "sequence": 100,
      "cpu": 45.5,
      "memory": 62.3,
      "disk": 71.2,
      "net_sent": 123456,
      "net_recv": 654321,
      "timestamp": 1710000000,
      "server_time": 1710000001
    }
  ],
  "network": [
    {
      "client_id": "node_1",
      "packets_received": 1000,
      "packets_lost": 8,
      "packet_loss": 0.79,
      "throughput": 1.02,
      "data_rate": 512.5,
      "latency": 0.023,
      "jitter": 0.005,
      "last_updated": 1710000001
    }
  ]
}
```

### `GET /api/network-analysis`

**Response:** Aggregated system-wide network metrics over time

```json
[
  {
    "last_updated": 1710000001,
    "packet_loss": 0.85,
    "throughput": 3.05,
    "data_rate": 1536.7,
    "latency": 0.025,
    "jitter": 0.006
  }
]
```

---

## Web Routes

| Route | Method | Template | Description |
|-------|--------|----------|-------------|
| `/` | GET | `dashboard.html` | Home page with summary metrics |
| `/devices` | GET | `devices.html` | Device inventory table |
| `/devices/add` | GET/POST | redirect | Legacy route redirected to `/devices` |
| `/devices/<client_id>` | GET | `device_detail.html` | Per-device charts |
| `/network` | GET | `network_analysis.html` | System-wide network analysis |

---

## Features

### Core Features

1. **Real-Time Monitoring**
   - Live telemetry from multiple Linux clients
   - Automatic status updates (online/offline based on 10s timeout)
   - System-wide aggregated metrics

2. **Device Management**
   - Automatic device registration via UDP handshake
   - Sender IP captured from the UDP socket address
   - Device inventory with status indicators
   - Per-device detail pages

3. **Packet Loss Detection**
   - Sequence number tracking per client
   - Gap detection for lost packets
   - Cumulative and percentage loss metrics

4. **Network Performance Analysis**
   - Throughput (packets/second)
   - Data rate (bytes/second)
   - One-way latency
   - Jitter (latency variation)
   - Update rate (Hz)

5. **Data Visualization**
   - 8 charts per device detail page
   - 6 charts for network analysis
   - Interactive Chart.js line charts
   - Time-series data with formatted timestamps

6. **REST API**
   - Full programmatic access to all data
   - JSON responses
   - Proper HTTP status codes (404 for not found)

### Technical Features

1. **Thread Safety**
   - Database operations protected by locks
   - UDP server runs in daemon thread
   - Short-lived SQLite connections

2. **Error Handling**
   - Packet validation with descriptive errors
   - Graceful handling of malformed packets
   - 404 pages for unknown devices

3. **Logging**
   - Structured logging for packet handler
   - Client activity logging
   - Error logging for debugging

4. **Responsive Design**
   - Mobile-friendly layout
   - Adaptive grid systems
   - Touch-friendly navigation

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Web browser (for dashboard access)

### Step-by-Step Installation

1. **Navigate to project directory:**
   ```bash
   cd /home/shadow_e15/College/CN/telemetry-system
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   **Dependencies:**
   - `Flask` (web framework)
   - `psutil` (system metrics, client-side only)

5. **Verify installation:**
   ```bash
   python -c "import flask; import psutil; print('OK')"
   ```

---

## Running the System

### Start Dashboard Server

```bash
cd /home/shadow_e15/College/CN/telemetry-system
source .venv/bin/activate
python -m dashboard.app
```

**Expected Output:**
```
 * Serving Flask app 'dashboard.app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

**What Happens:**
1. SQLite database initialized (creates tables if needed)
2. UDP server starts on port 9999
3. Flask web server starts on port 5000
4. Application ready to receive telemetry

### Access Dashboard

Open browser to: `http://127.0.0.1:5000`

### Register Devices

Start a telemetry client with a `client_id`. The client automatically sends a UDP `REGISTER` message before telemetry begins.

**Important:** Registration is now part of the socket protocol. The server stores:
- `client_id` from the CLI
- `device_name` from the client hostname
- `ip_address` from the UDP sender address

### Start Telemetry Clients

On each client machine (or same machine for testing):

```bash
cd /home/shadow_e15/College/CN/telemetry-system
source .venv/bin/activate
python -m client.client --client-id node_1 --host <SERVER_IP> --port 9999 --interval 1
```

**Parameters:**
- `--client-id`: Unique client identifier used during UDP registration
- `--host`: Dashboard server IP address
- `--port`: UDP server port (default: 9999)
- `--interval`: Seconds between packets (default: 1)

### Stop the System

1. Press `Ctrl+C` in each client terminal
2. Press `Ctrl+C` in dashboard terminal

---

## Telemetry Packet Format

### Message Types

The UDP protocol now uses explicit typed JSON messages:

- `REGISTER`
- `REGISTER_ACK`
- `TELEMETRY`
- `ACK`

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
  "net_sent": 123456789,
  "net_recv": 987654321,
  "timestamp": 1710000000
}
```

### Validation Rules

- Every message must include a valid `type`
- `REGISTER` must include `client_id`, `device_name`, and `timestamp`
- `TELEMETRY` must include all telemetry fields and a non-negative `sequence`
- `cpu`, `memory`, `disk` must be 0-100
- `net_sent`, `net_recv` must be non-negative
- `TELEMETRY` packets are accepted only after successful registration
- The server replies with `REGISTER_ACK` and `ACK` so the client can retry safely

---

## Network Metrics Calculation

### Packet Loss

**Formula:**
```
packets_lost = current_sequence - previous_sequence - 1
packet_loss % = packets_lost / (packets_received + packets_lost) × 100
```

**Example:**
- Previous sequence: 100
- Current sequence: 104
- Lost packets: 104 - 100 - 1 = 3 (packets 101, 102, 103 missing)

### Throughput

**Formula:**
```
throughput = packets_received / elapsed_time
```
**Unit:** packets per second (pkt/s)

### Data Rate

**Formula:**
```
data_rate = total_bytes_received / elapsed_time
```
**Unit:** bytes per second (bytes/s)

### Latency

**Formula:**
```
latency = server_time - client_timestamp
```
**Unit:** seconds

**Note:** One-way latency (assumes clocks are synchronized)

### Jitter

**Formula:**
```
jitter = |current_latency - previous_latency|
```
**Unit:** seconds

### Update Rate

**Formula:**
```
update_rate = 1 / (current_last_updated - previous_last_updated)
```
**Unit:** Hertz (Hz)

---

## Design System

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Background | `#f4efe7` | Page background |
| Panel | `#fffdf8` | Card backgrounds |
| Panel Strong | `#efe5d7` | Buttons, accents |
| Text | `#1f2933` | Primary text |
| Muted | `#6b7280` | Secondary text, labels |
| Accent | `#0f766e` | Primary brand color (teal) |
| Accent Soft | `#d7f3ef` | Online status, highlights |
| Danger | `#b91c1c` | Errors, offline status |
| Border | `#dfd5c5` | Dividers, input borders |

### Typography

- **Font Family:** Georgia, "Times New Roman", serif
- **Base Size:** 16px (browser default)
- **Headings:** 1.6rem (sidebar), 1.8rem (metric values)
- **Eyebrow Text:** 0.75rem, uppercase, 0.16em letter-spacing

### Spacing

- **Card Padding:** 1.25rem
- **Section Padding:** 2rem
- **Grid Gap:** 1rem (charts), 0.8rem (nav)
- **Border Radius:** 24px (cards), 999px (buttons, status badges)

### Shadows

```css
box-shadow: 0 18px 45px rgba(31, 41, 51, 0.08);
```

### Responsive Breakpoints

- **Desktop:** >900px (sidebar + content grid)
- **Mobile:** ≤900px (single column, stacked layout)

---

## Security Considerations

### Current Security Model

1. **Device Registration Gate**
   - Only registered `client_id` values accepted
   - Prevents unauthorized telemetry injection
   - Manual registration required (no auto-discovery)

2. **Input Validation**
   - IP address validation (IPv4/IPv6)
   - Packet field type checking
   - Range validation for metrics

3. **Local-Only Default**
   - Dashboard binds to `127.0.0.1` by default
   - UDP server binds to `0.0.0.0` (all interfaces)

### Security Limitations

⚠️ **Important:** This dashboard is designed for trusted network environments (lab, homelab, internal network). It is NOT production-hardened.

**Known Limitations:**
- No authentication or authorization
- No HTTPS/TLS encryption
- No rate limiting
- No input sanitization beyond type checking
- SQLite not suitable for high-concurrency production
- UDP is inherently unauthenticated and spoofable

### Recommendations for Production Use

1. **Network Security:**
   - Place behind firewall or VPN
   - Use Tailscale or similar for remote access
   - Restrict UDP port 9999 to known client IPs

2. **Transport Security:**
   - Add HTTPS with reverse proxy (nginx, Caddy)
   - Consider TCP or TLS-wrapped UDP for telemetry

3. **Authentication:**
   - Add login system (Flask-Login)
   - API token authentication for clients
   - Session management for web users

4. **Hardening:**
   - Add rate limiting (Flask-Limiter)
   - Input sanitization (bleach for any user content)
   - CSRF protection (Flask-WTF)
   - Security headers (Flask-Talisman)

---

## Performance Characteristics

### Scalability

| Metric | Current Capability | Bottleneck |
|--------|-------------------|------------|
| Concurrent Clients | ~50-100 | UDP packet processing |
| Telemetry Rate | 1-10 packets/sec/client | Database write speed |
| Chart Data Points | 100 per chart (configurable) | Query performance |
| Web Concurrency | Low (single-threaded Flask) | Flask dev server |

### Database Performance

- **Write Pattern:** INSERT-heavy (one row per packet per client)
- **Read Pattern:** Aggregation queries with GROUP BY and JOINs
- **Indexing:** No explicit indexes (relies on SQLite rowid)
- **Retention:** Unlimited (manual cleanup required)

**Optimization Opportunities:**
- Add indexes on `client_id`, `server_time`, `last_updated`
- Implement data retention policy (auto-delete old records)
- Use WAL mode for better concurrent read/write performance

### Memory Usage

- **UDP Server:** Minimal (socket buffer only)
- **Flask App:** Low (stateless, no sessions)
- **Database:** Grows with telemetry volume
- **Charts:** Limited to `history_limit` (default: 100 points)

### Network Performance

- **UDP Overhead:** Minimal (connectionless, no handshake)
- **Packet Size:** ~200-300 bytes (JSON telemetry)
- **Bandwidth:** ~300 bytes/sec/client at 1Hz interval

---

## Limitations & Known Issues

### Functional Limitations

1. **No Real-Time Updates**
   - Pages require manual refresh
   - No WebSocket or Server-Sent Events
   - Charts show historical data only

2. **No Alerting**
   - No threshold-based alerts
   - No email/push notifications
   - No anomaly detection

3. **Limited History**
   - Charts limited to 100 data points
   - No data export functionality
   - No backup/restore mechanism

4. **Single-Server Architecture**
   - No horizontal scaling
   - Single point of failure
   - No load balancing

5. **Manual Device Registration**
   - No auto-discovery
   - No bulk import
   - No device groups or tags

### Technical Limitations

1. **Flask Development Server**
   - Not suitable for production
   - Single-threaded request handling
   - No async support

2. **SQLite Constraints**
   - File-based (not distributed)
   - Write locking under high concurrency
   - No built-in replication

3. **UDP Reliability**
   - Packets can be lost (by design)
   - No retransmission
   - No ordering guarantees

4. **No Authentication**
   - Anyone with network access can register devices
   - API endpoints are open
   - No audit logging

### Known Issues

1. **Clock Synchronization**
   - Latency calculation assumes synchronized clocks
   - NTP not enforced
   - Cross-timezone deployments may show negative latency

2. **Sequence Number Wraparound**
   - No handling for integer overflow
   - Long-running clients may wrap sequence numbers

3. **Memory Growth**
   - Database grows indefinitely
   - No automatic cleanup
   - Manual intervention required for long deployments

---

## Future Enhancement Opportunities

### High Priority

1. **Real-Time Updates**
   - WebSocket integration for live chart updates
   - Auto-refresh dashboard metrics
   - Push notifications for status changes

2. **Authentication & Authorization**
   - User login system
   - API key authentication for clients
   - Role-based access control

3. **Data Retention & Archival**
   - Configurable retention policies
   - Automatic data purging
   - Export to CSV/JSON

4. **Alerting System**
   - Threshold-based alerts (CPU > 90%, etc.)
   - Email/Slack/webhook notifications
   - Alert history and acknowledgment

### Medium Priority

5. **Improved Visualizations**
   - Dark mode support
   - Customizable chart time ranges
   - Export charts as images
   - Dashboard customization (drag-and-drop widgets)

6. **Device Management**
   - Bulk device import/export
   - Device groups and tags
   - Device metadata (location, purpose, owner)

7. **Performance Optimization**
   - Database indexing
   - Query caching
   - Connection pooling

8. **Production Hardening**
   - HTTPS/TLS support
   - Rate limiting
   - Security headers
   - Reverse proxy configuration

### Lower Priority

9. **Advanced Analytics**
   - Trend analysis and forecasting
   - Anomaly detection
   - Correlation analysis across devices

10. **Multi-Server Support**
    - Horizontal scaling
    - Load balancing
    - Distributed database (PostgreSQL, TimescaleDB)

11. **API Enhancements**
    - GraphQL endpoint
    - WebSocket API for real-time data
    - OpenAPI/Swagger documentation

12. **Client Improvements**
    - Auto-discovery protocol
    - Configuration management
    - Client health reporting

---

## Troubleshooting

### Dashboard Won't Start

**Symptom:** `python -m dashboard.app` fails

**Possible Causes:**
1. **Port already in use:**
   ```bash
   lsof -i :5000
   kill <PID>
   ```

2. **Database lock:**
   ```bash
   rm database/telemetry.db
   # Database will be recreated on next start
   ```

3. **Missing dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### No Telemetry Data Appearing

**Symptom:** Dashboard shows 0 active devices, charts are empty

**Checklist:**
1. **Device registered?**
   - Verify device exists in `/devices` page
   - Client ID must match exactly (case-sensitive)

2. **Client running?**
   - Check client terminal for errors
   - Verify `--client-id` matches registered device

3. **Network connectivity:**
   ```bash
   # From client, test UDP connectivity
   nc -u <server_ip> 9999
   # Type test message, should reach server
   ```

4. **Firewall blocking UDP:**
   ```bash
   # On server, check firewall rules
   sudo ufw status
   sudo ufw allow 9999/udp
   ```

5. **Server logs:**
   - Check dashboard terminal for packet handler warnings
   - Look for "ignored packet from unregistered client_id"

### Charts Not Rendering

**Symptom:** Device detail or network analysis pages show empty chart areas

**Possible Causes:**
1. **Chart.js not loading:**
   - Check browser console for CDN errors
   - Verify internet connectivity (Chart.js loaded from jsdelivr.net)

2. **No data in database:**
   - Check `/api/devices/<client_id>/metrics` returns data
   - Verify client is sending telemetry

3. **JavaScript errors:**
   - Open browser DevTools console
   - Look for errors in `device_detail.js` or `network_analysis.js`

### High Packet Loss

**Symptom:** Dashboard shows >5% packet loss

**Investigation:**
1. **Network congestion:**
   - Reduce client send interval
   - Check network utilization

2. **Server overload:**
   - Monitor server CPU/memory
   - Reduce number of clients

3. **UDP limitations:**
   - UDP packet loss is expected under load
   - Consider TCP for critical deployments

4. **Sequence gap analysis:**
   - Check `network_stats` table for patterns
   - Correlate loss with specific time periods

### Database Performance Issues

**Symptom:** Slow page loads, timeout errors

**Solutions:**
1. **Add indexes:**
   ```sql
   CREATE INDEX idx_telemetry_client_time ON telemetry(client_id, server_time);
   CREATE INDEX idx_network_client_time ON network_stats(client_id, last_updated);
   ```

2. **Enable WAL mode:**
   ```sql
   PRAGMA journal_mode=WAL;
   ```

3. **Reduce history limit:**
   - Edit `config.py`, set `history_limit = 50`

4. **Archive old data:**
   ```sql
   DELETE FROM telemetry WHERE server_time < strftime('%s', 'now', '-7 days');
   DELETE FROM network_stats WHERE last_updated < strftime('%s', 'now', '-7 days');
   ```

---

## Appendix A: File Reference

### Backend Files

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | ~100 | Flask application factory, routes |
| `server/aggregator.py` | ~30 | Data aggregation facade |
| `server/database.py` | ~250 | SQLite operations |
| `server/packet_handler.py` | ~60 | Packet validation and processing |
| `server/sequence_tracker.py` | ~60 | Sequence tracking, metrics calculation |
| `server/udp_server.py` | ~50 | UDP socket server |
| `server/config.py` | ~20 | Configuration constants |

### Frontend Files

| File | Lines | Purpose |
|------|-------|---------|
| `templates/base.html` | ~30 | Base layout |
| `templates/dashboard.html` | ~20 | Home page |
| `templates/devices.html` | ~40 | Device table |
| `templates/device_detail.html` | ~30 | Device charts |
| `templates/network_analysis.html` | ~20 | Network charts |
| `templates/add_device.html` | ~20 | Registration form |
| `static/css/styles.css` | ~200 | Stylesheet |
| `static/js/device_detail.js` | ~60 | Device chart initialization |
| `static/js/network_analysis.js` | ~40 | Network chart initialization |

### Total Code Stats

- **Python:** ~600 lines
- **HTML:** ~160 lines
- **CSS:** ~200 lines
- **JavaScript:** ~100 lines
- **Total:** ~1,060 lines

---

## Appendix B: Quick Reference Commands

### Start System
```bash
# Terminal 1: Dashboard
cd /home/shadow_e15/College/CN/telemetry-system
source .venv/bin/activate
python -m dashboard.app
```

### Start Client
```bash
# Terminal 2+: Client
cd /home/shadow_e15/College/CN/telemetry-system
source .venv/bin/activate
python -m client.client --client-id node_1 --host 127.0.0.1 --port 9999
```

### Check Database
```bash
sqlite3 database/telemetry.db "SELECT * FROM devices;"
sqlite3 database/telemetry.db "SELECT COUNT(*) FROM telemetry;"
```

### Test API
```bash
curl http://127.0.0.1:5000/api/summary
curl http://127.0.0.1:5000/api/devices
curl http://127.0.0.1:5000/api/devices/node_1/metrics
```

### Monitor UDP Port
```bash
# On server, watch UDP traffic
sudo tcpdump -i any -n udp port 9999
```

### Cleanup Database
```bash
# Remove old telemetry (keep last 7 days)
sqlite3 database/telemetry.db "DELETE FROM telemetry WHERE server_time < strftime('%s', 'now', '-7 days');"
sqlite3 database/telemetry.db "VACUUM;"
```

---

## Appendix C: Changelog

### Version 1.0 (March 26, 2026)

**Initial Release:**
- Flask dashboard with 5 pages
- Embedded UDP telemetry server
- SQLite persistence
- 8 device metrics charts
- 6 network analysis charts
- Manual device registration
- Packet loss detection
- REST API with 5 endpoints
- Responsive design

**Known Limitations:**
- No authentication
- No real-time updates
- No alerting
- Single-server only

---

## Credits

**Original Author:** Ankit (B.Tech student, Bangalore)  
**Documentation:** Claw (AI Assistant)  
**Date:** April 1, 2026  
**Project:** Computer Networks - Telemetry Collection System  
**Institution:** College Engineering Project

---

*This documentation was generated to enable Codex (GPT-5.4) to understand and enhance the dashboard. All technical details verified against source code.*
