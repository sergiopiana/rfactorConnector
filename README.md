# SimRacing Universal Connector

A modular, multi-game telemetry connector that exposes physics data (Speed, RPM, Gear, Pedals, etc.) via a standardized WebSocket API. 

Designed to let you build ANY hardware or software integration (Wind Simulators, Motion Rigs, Dashboards, Hue Sync, etc.) without worrying about the specific game API.

## Supported Games

- **iRacing** (via generic PyIrSdk)
- **Assetto Corsa** (via Shared Memory)
- **rFactor 1 / Automobilista** (via `rFactorSharedMemoryMap.dll`)
- **BeamNG.drive** (via OutGauge UDP)

## Architecture

The connector acts as a **Server**. 
1. It connects to the requested Game.
2. It normalizes data into a standard JSON Structure.
3. It broadcasts this JSON to all connected WebSocket clients (port 8765 by default).

## Installation

1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    pip install pyirsdk # Required for iRacing
    ```

## Usage

Start the connector for your specific game:

```bash
python main.py --game iracing
```

Available games: `iracing`, `ac`, `rfactor`, `beamng`, `test`.

## API (WebSocket)

Connect to `ws://localhost:8765`. You will receive a JSON stream at ~60Hz:

```json
{
  "game_name": "Assetto Corsa",
  "connected": true,
  "speed_kmh": 120.5,
  "rpm": 5400,
  "max_rpm": 8000,
  "gear": 3,
  "throttle": 1.0,
  "brake": 0.0,
  "clutch": 0.0,
  "steering_angle": 0.05
}
```

## Examples

### Wind Simulator (Legacy Mode)
If you want to use this for a Wind Simulator (controlling an ESP32), see `examples/wind_sim_client.py`.

1. Run the connector: `python main.py --game <game>`
2. Run the client: `python examples/wind_sim_client.py`

This separates the Game Logic from the Hardware Logic.
