from abc import ABC, abstractmethod
from core.telemetry import TelemetryData

class GameProvider(ABC):
    """Base interface for all game providers"""
    
    @abstractmethod
    def get_telemetry(self) -> TelemetryData:
        """
        Reads data from the game and returns a standard TelemetryData object.
        Should return a TelemetryData with connected=False if game is not running.
        """
        pass
