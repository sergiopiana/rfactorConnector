import socket
import struct
from providers import GameProvider
from core.telemetry import TelemetryData

class BeamNGProvider(GameProvider):
    def __init__(self, port=4444):
        self.game_name = "BeamNG.drive"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind(('127.0.0.1', port))
            self.sock.setblocking(False)
            print(f"Initialized {self.game_name} Provider (UDP {port})")
        except OSError:
            print(f"Error binding to port {port}. Is it already in use?")

    def get_telemetry(self) -> TelemetryData:
        try:
            # We need to drain the socket to get the LATEST packet
            data = None
            while True:
                try:
                    d, _ = self.sock.recvfrom(1024)
                    data = d
                except BlockingIOError:
                    break
            
            if data is None:
                return TelemetryData(self.game_name, False) # No new data

            # OutGauge Structure (LFS standard)
            # Time(4), Car(4), Flags(2), Gear(1), PLID(1), Speed(4), RPM(4), Turbo(4), EngTemp(4) ...
            # Speed offset: 12
            # RPM offset: 16
            
            if len(data) >= 20:
                speed_ms = struct.unpack('f', data[12:16])[0]
                rpm = struct.unpack('f', data[16:20])[0]
                gear = data[10] # Byte
                
                return TelemetryData(
                    game_name=self.game_name,
                    connected=True,
                    speed_kmh=speed_ms * 3.6,
                    rpm=rpm,
                    max_rpm=8000, # Unknown in OutGauge?
                    gear=gear,
                    throttle=0, # Needs parsing flags or extra data
                    brake=0,
                    clutch=0
                )
        except Exception as e:
            pass
            
        return TelemetryData(self.game_name, False)
