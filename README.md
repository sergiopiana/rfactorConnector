# Wind Simulator Bridge & rFactor Connector

This project allows you to connect various racing simulators (rFactor, iRacing, Assetto Corsa, BeamNG) to an ESP32-based wind simulator. It reads telemetry data (speed) from the game and sends it via UDP to the ESP32 to control fan speed. It also broadcasts telemetry via WebSockets.

## Features

- **Multi-Game Support**:
  - rFactor 1 (via Shared Memory)
  - iRacing (via API)
  - Assetto Corsa (via Shared Memory)
  - BeamNG.drive (via OutGauge UDP)
- **ESP32 Integration**: Sends UDP packets to control PWM fans.
- **WebSocket Server**: Broadcasts telemetry data for local dashboards or debugging.

## Prerequisites

- Python 3.x
- An ESP32 running the compatible wind simulator firmware.

## Installation

1.  Clone this repository.
2.  Install the required Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    *Note: For iRacing support, you also need to install `pyirsdk`:*
    ```bash
    pip install pyirsdk
    ```

## Configuration

Open `bridge.py` and configure the following settings at the top of the file:

```python
# --- CONFIGURATION ---
ESP_IP = "192.168.68.80" # REPLACE WITH YOUR ESP32 IP
ESP_PORT = 4210
MAX_SPEED_KMH = 200 # Speed at which fans reach 100%
```

## Usage

Run the bridge script from the command line, specifying the game you are playing:

```bash
python bridge.py --game <game_name>
```

### Supported Games & Arguments

-   **rFactor**: `--game rfactor`
    -   **Requirement**: You must install the `rFactorSharedMemoryMap.dll` plugin into your `rFactor/Plugins` directory.
-   **iRacing**: `--game iracing`
    -   **Requirement**: iRacing sim must be running.
-   **Assetto Corsa**: `--game ac`
    -   **Requirement**: Shared Memory must be enabled in AC settings (usually on by default).
-   **BeamNG.drive**: `--game beamng`
    -   **Requirement**: Enable 'OutGauge' in BeamNG Hardware settings. Set IP to `127.0.0.1` and Port to `4444`.
-   **Test Mode**: `--game test`
    -   Generates a sine wave speed signal to test the fans without a game.

## Troubleshooting

-   **Fans not spinning**:
    -   Check if the ESP32 IP in `bridge.py` matches your device's IP.
    -   Ensure the ESP32 is powered and connected to WiFi.
    -   Verify the computer firewall is not blocking UDP port 4210.
-   **rFactor not connecting**:
    -   Ensure the DLL plugin is in the correct folder (`rFactor/Plugins`) and unlocked if necessary.
    -   Run rFactor as Administrator.
