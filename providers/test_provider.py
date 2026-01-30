import math
import time
from providers import GameProvider
from core.telemetry import TelemetryData

class TestProvider(GameProvider):
    def __init__(self):
        self.t = 0
        self.game_name = "TestProvider"
        print(f"Initialized {self.game_name} (Sine Wave Generators)")

    def get_telemetry(self) -> TelemetryData:
        # Speed sine wave (0 to 250 km/h)
        speed = ((math.sin(self.t * 0.1) + 1) / 2) * 250
        
        # RPM sawtooth (0 to 8000)
        rpm = (self.t * 100) % 8000
        
        # Gear steps 1-6
        gear = int((speed / 250) * 6) + 1
        
        self.t += 0.5
        
        return TelemetryData(
            game_name=self.game_name,
            connected=True,
            speed_kmh=speed,
            rpm=rpm,
            max_rpm=8000,
            gear=gear,
            throttle=(math.sin(self.t * 0.05) + 1) / 2,
            brake=0,
            clutch=0
        )
