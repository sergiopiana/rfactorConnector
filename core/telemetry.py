from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class TelemetryData:
    """Standardized Telemetry Data Structure"""
    game_name: str
    connected: bool
    speed_kmh: float = 0.0
    rpm: float = 0.0
    max_rpm: float = 0.0
    gear: int = 0
    throttle: float = 0.0
    brake: float = 0.0
    clutch: float = 0.0
    
    # Optional/Extended physics
    steering_angle: float = 0.0
    
    def to_dict(self):
        return asdict(self)
