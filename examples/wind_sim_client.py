import asyncio
import websockets
import json
import socket
import argparse

# --- CONFIGURATION ---
ESP_IP = "192.168.68.80" # REPLACE WITH YOUR ESP32 IP
ESP_PORT = 4210
MAX_SPEED_KMH = 200 # Speed at which fans reach 100%

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

async def listen_to_connector():
    uri = "ws://localhost:8765"
    controller = FanController(ESP_IP, ESP_PORT)
    
    print(f"Connecting to SimRacing Connector at {uri}...")
    print(f"Forwarding to ESP32 at {ESP_IP}:{ESP_PORT}")
    
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data.get("connected"):
                    speed = data.get("speed_kmh", 0)
                    controller.send_speed(speed)
                else:
                    # Game not running
                    controller.send_speed(0)
                    
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed. Retrying in 2s...")
                await asyncio.sleep(2)
                continue
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(listen_to_connector())
    except KeyboardInterrupt:
        print("\nStopped.")
