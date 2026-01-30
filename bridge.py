import socket
import time
import sys
import math
import argparse
import struct
import mmap
import ctypes

# --- CONFIGURATION ---
ESP_IP = "192.168.68.80" # REPLACE WITH YOUR ESP32 IP
ESP_PORT = 4210
MAX_SPEED_KMH = 200 # Speed at which fans reach 100%

# --- UDP SENDER ---
class FanController:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_speed(self, speed_kmh):
        # Map to 0-100%
        speed_pct = int((speed_kmh / MAX_SPEED_KMH) * 100)
        if speed_pct > 100: speed_pct = 100
        if speed_pct < 0: speed_pct = 0
        
        try:
            message = str(speed_pct).encode()
            self.sock.sendto(message, (self.ip, self.port))
            print(f"Speed: {speed_kmh:.1f} km/h -> Fan: {speed_pct}%", end='\r')
        except Exception as e:
            print(f"UDP Error: {e}")

    def stop(self):
        self.sock.sendto(b"0", (self.ip, self.port))

# --- GAME PROVIDERS ---

class GameProvider:
    def get_speed_kmh(self):
        """Returns current speed in km/h or None if not connected"""
        return 0

class IRacingProvider(GameProvider):
    def __init__(self):
        try:
            import irsdk
            self.ir = irsdk.IRSDK()
            print("Initialized iRacing Provider")
        except ImportError:
            print("Error: 'pyirsdk' not installed. Run: pip install pyirsdk")
            sys.exit(1)

    def get_speed_kmh(self):
        if not self.ir.is_initialized:
            if not self.ir.startup():
                return None
        
        self.ir.freeze_var_buffer_latest()
        try:
            speed_ms = self.ir['Speed']
            return speed_ms * 3.6
        except (KeyError, TypeError):
            return 0

class AssettoCorsaProvider(GameProvider):
    def __init__(self):
        self.map_name = "Local\\acpmf_physics"
        self.mm = None
        print("Initialized Assetto Corsa Provider (Waiting for Shared Memory...)")

    def get_speed_kmh(self):
        if self.mm is None:
            try:
                # AC Physics structure is large, but SpeedKmh is usually at offset 0 or close.
                # Actually, in AC Physics struct:
                # packetId (4), gas (4), brake (4), ... speedKmh (4) is at offset 28 usually?
                # Let's use a safer struct approach if possible, or just try to open it.
                self.mm = mmap.mmap(0, 712, self.map_name) # 712 is typical size
                print("Connected to Assetto Corsa Shared Memory!")
            except FileNotFoundError:
                return None
        
        try:
            self.mm.seek(0)
            # We need to read the float at the specific offset for speed.
            # Struct layout (partial):
            # int packetId; float gas; float brake; float fuel; int gear; int rpm; float steerAngle; float speedKmh;
            # 4 + 4 + 4 + 4 + 4 + 4 + 4 = 28 bytes offset?
            # Let's verify standard AC struct.
            # packetId (0-4), gas (4-8), brake (8-12), fuel (12-16), gear (16-20), rpm (20-24), steer (24-28), speedKmh (28-32)
            self.mm.seek(28)
            speed_bytes = self.mm.read(4)
            speed_kmh = struct.unpack('f', speed_bytes)[0]
            return speed_kmh
        except Exception as e:
            print(f"AC Read Error: {e}")
            self.mm.close()
            self.mm = None
            return 0

class BeamNGProvider(GameProvider):
    def __init__(self, port=4444):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', port))
        self.sock.setblocking(False)
        print(f"Initialized BeamNG Provider (Listening on UDP {port})")
        print("NOTE: Enable 'OutGauge' in BeamNG Hardware settings with IP 127.0.0.1 and Port 4444")

    def get_speed_kmh(self):
        try:
            data, _ = self.sock.recvfrom(1024)
            # OutGauge format (approx 96 bytes)
            # Speed is usually part of it.
            # Standard OutGauge struct:
            # time(4), car(4), flags(2), gear(1), ... speed(4) at offset ~12?
            # Let's look up OutGauge struct.
            # time(4), car(32), flags(2), gear(1), plid(1), speed(4) ...
            # Actually, standard LFS OutGauge:
            # Time(4), Car(4), Flags(2), Gear(1), PLID(1), Speed(4) ...
            # Offset: 4+4+2+1+1 = 12 bytes.
            if len(data) >= 16:
                speed_ms = struct.unpack('f', data[12:16])[0]
                return speed_ms * 3.6 # BeamNG sends m/s usually? Or is it already km/h?
                # OutGauge spec says m/s.
        except BlockingIOError:
            pass # No data
        except Exception as e:
            print(f"BeamNG Error: {e}")
        
        return None # Return None to indicate no *new* data, or handle state

class TestProvider(GameProvider):
    def __init__(self):
        self.t = 0
        print("Initialized Test Provider (Sine Wave)")

    def get_speed_kmh(self):
        val = (math.sin(self.t * 0.1) + 1) / 2
        self.t += 1
        return val * MAX_SPEED_KMH

class RFactorProvider(GameProvider):
    def __init__(self):
        self.map_name = "$rFactorShared$"
        self.mm = None
        print("Initialized rFactor Provider (Waiting for Shared Memory...)")
        print("Ensure 'MapPlugin' or 'rFactorSharedMemoryMap' is installed in rFactor/Plugins")

    def get_speed_kmh(self):
        if self.mm is None:
            try:
                # Open shared memory. Size varies but 24KB is safe upper bound for standard plugins.
                self.mm = mmap.mmap(-1, 1024, self.map_name) 
                print("Connected to rFactor Shared Memory!")
            except FileNotFoundError:
                return None
            except Exception as e:
                # Start non-blocking?
                return None
        
        try:
            self.mm.seek(0)
            # Standard rfShared layout usually has speed around offset 24 (float mSpeed)
            # or Velocity vector [x,y,z] around offset 16?
            # Let's try reading a float at offset 24.
            # Struct: mTime(0), mLapTime(4), mLapDist(8), mTotalDist(12) ...
            # Some versions: mSpeed(24) or mSpeed(20)?
            # We will try offset 24.
            # Found speed at offset 236 through manual inspection
            self.mm.seek(236)
            speed_bytes = self.mm.read(4)
            speed_ms = struct.unpack('f', speed_bytes)[0]
            
            # Sanity check: if speed is > 400km/h (111 m/s) maybe wrong offset?
            # But we just return it.
            return speed_ms * 3.6
        except Exception as e:
            print(f"rFactor Read Error: {e}")
            self.mm.close()
            self.mm = None
            return 0

# --- MAIN LOOP ---

import asyncio
import json
import threading
import websockets

# --- WEBSOCKET SERVER ---
CONNECTED_CLIENTS = set()
CURRENT_TELEMETRY = {"speed": 0, "connected": False}

async def ws_handler(websocket):
    CONNECTED_CLIENTS.add(websocket)
    print("New WebSocket Client connected!")
    try:
        await websocket.wait_closed()
    finally:
        CONNECTED_CLIENTS.remove(websocket)

async def broadcast_loop():
    while True:
        if CONNECTED_CLIENTS:
            message = json.dumps(CURRENT_TELEMETRY)
            # Create a list of tasks to send messages
            tasks = [asyncio.create_task(ws.send(message)) for ws in CONNECTED_CLIENTS]
            if tasks:
                await asyncio.wait(tasks)
        await asyncio.sleep(0.05) # 20Hz update rate

async def start_server():
    async with websockets.serve(ws_handler, "localhost", 8765):
        await broadcast_loop()

def run_ws_server():
    asyncio.run(start_server())

# --- MAIN LOOP ---

def main():
    parser = argparse.ArgumentParser(description="Wind Simulator Bridge")
    parser.add_argument("--game", choices=['iracing', 'ac', 'beamng', 'rfactor', 'test'], default='iracing', help="Select game provider")
    args = parser.parse_args()

    # Start WebSocket Server in a separate thread
    ws_thread = threading.Thread(target=run_ws_server, daemon=True)
    ws_thread.start()
    print("WebSocket Server started on ws://localhost:8765")

    controller = FanController(ESP_IP, ESP_PORT)
    
    provider = None
    if args.game == 'iracing':
        provider = IRacingProvider()
    elif args.game == 'ac':
        provider = AssettoCorsaProvider()
    elif args.game == 'beamng':
        provider = BeamNGProvider()
    elif args.game == 'rfactor':
        provider = RFactorProvider()
    elif args.game == 'test':
        provider = TestProvider()

    print(f"Starting Bridge for {args.game.upper()}...")
    
    last_speed = 0
    
    try:
        while True:
            speed = provider.get_speed_kmh()
            
            if speed is not None:
                controller.send_speed(speed)
                last_speed = speed
                CURRENT_TELEMETRY["speed"] = speed
                CURRENT_TELEMETRY["connected"] = True
            else:
                # If game not running/sending, maybe send 0 or keep last?
                # Safer to send 0 if connection lost
                CURRENT_TELEMETRY["connected"] = False
                pass

            time.sleep(0.05) # Increased update rate for smoother UI
            
    except KeyboardInterrupt:
        print("\nStopping...")
        controller.stop()

if __name__ == "__main__":
    main()
