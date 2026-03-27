# Telemetry System Program Explanation

This file explains what each program in the telemetry project does.

Project folder:

```text
telemetry-system/
```

## 1. `server.py`

Purpose:

- Runs the central UDP telemetry server.

What it does:

- Creates a UDP socket using Python's `socket` module.
- Binds the socket to the configured host and port.
- Continuously listens for incoming telemetry packets.
- Decodes each packet.
- Validates packet contents.
- Tracks the last sequence number for each client.
- Detects packet loss by checking for sequence gaps.
- Updates total packet counters.
- Aggregates CPU, memory, and disk metrics.
- Prints periodic performance statistics.

Important parts:

- `TelemetryServer` class manages the full server workflow.
- `_handle_packet()` processes each received packet.
- `_report_stats_loop()` prints statistics every few seconds.
- `print_stats()` displays client-wise and overall metrics.

## 2. `client.py`

Purpose:

- Simulates a distributed telemetry client.

What it does:

- Creates a UDP socket.
- Accepts a unique client ID from the command line.
- Maintains a packet sequence number.
- Generates fake telemetry data periodically.
- Builds a telemetry packet.
- Encodes the packet to JSON bytes.
- Sends the packet to the server.
- Repeats this continuously at a configurable interval.

Important parts:

- `TelemetryClient` class handles packet creation and sending.
- `send_forever()` repeatedly sends telemetry packets.
- `parse_args()` reads command-line options like client ID, host, port, and interval.

## 3. `telemetry_generator.py`

Purpose:

- Simulates system telemetry values.

What it does:

- Randomly generates CPU usage.
- Randomly generates memory usage.
- Randomly generates disk usage.
- Adds a current timestamp.
- Returns all values as one metrics dictionary.

Functions:

- `generate_cpu_usage()`
- `generate_memory_usage()`
- `generate_disk_usage()`
- `generate_metrics()`

Why it is useful:

- It makes the clients behave like real nodes producing monitoring data.

## 4. `packet_utils.py`

Purpose:

- Handles packet formatting and validation.

What it does:

- Converts Python dictionaries into JSON bytes before sending.
- Converts received JSON bytes back into Python dictionaries.
- Validates whether a packet has all required fields.
- Checks correct data types for fields like `client_id`, `sequence`, and metric values.
- Raises a custom `PacketError` if a packet is invalid.

Functions:

- `encode_packet()`
- `decode_packet()`
- `validate_packet()`

Why it is useful:

- It keeps packet handling logic separate from client and server logic.
- It improves code cleanliness and reliability.

## 5. `config.py`

Purpose:

- Stores configuration values in one place.

What it does:

- Defines the default server host.
- Defines the default server port.
- Defines packet size.
- Defines client sending interval.
- Defines server statistics print interval.
- Defines socket timeout.

Why it is useful:

- If you want to change the port or timing, you edit one file instead of changing many files.

## 6. `metrics.py`

Purpose:

- Performs telemetry aggregation and performance measurement.

What it does:

### `TelemetryAggregator`

- Stores total CPU values.
- Stores total memory values.
- Stores total disk values.
- Stores the number of received samples.
- Computes average CPU, memory, and disk usage.

### `PerformanceMonitor`

- Tracks total packets received.
- Tracks total packets lost.
- Tracks packets received per client.
- Stores the last sequence number for each client.
- Stores lost packets per client.
- Calculates throughput in packets per second.
- Calculates packet loss rate.

Why it is useful:

- It separates statistics logic from the networking logic.
- It makes the code modular and easier to maintain.

## 7. `requirements.txt`

Purpose:

- Lists project dependencies.

What it does:

- Currently contains no external packages because the project uses only built-in Python libraries.

Why it is included:

- It is standard practice in Python projects.
- It makes the project structure complete and ready for future extensions.

## 8. `README.md`

Purpose:

- Gives project overview and usage instructions.

What it contains:

- Project description
- Features
- Folder structure
- Installation steps
- Configuration details
- Commands to run the server and clients
- Example packet format
- Example server output

Why it is useful:

- It helps anyone understand and run the project quickly.

## 9. How All Files Work Together

Flow of the project:

1. `client.py` asks `telemetry_generator.py` to generate metrics.
2. `client.py` asks `packet_utils.py` to encode the packet.
3. `client.py` sends the UDP packet to `server.py`.
4. `server.py` receives the packet.
5. `server.py` asks `packet_utils.py` to decode and validate it.
6. `server.py` uses `metrics.py` to update counters and averages.
7. `server.py` prints performance and telemetry statistics.
8. `config.py` provides the default values used by both server and client.

## 10. Short One-Line Summary for Each File

- `server.py`: receives telemetry data and computes server-side statistics.
- `client.py`: sends telemetry data continuously to the server.
- `telemetry_generator.py`: creates fake CPU, memory, and disk usage values.
- `packet_utils.py`: handles packet encoding, decoding, and validation.
- `config.py`: stores all configurable default values.
- `metrics.py`: calculates averages, throughput, and packet loss.
- `requirements.txt`: lists dependencies, currently none.
- `README.md`: explains how to install, run, and understand the project.

