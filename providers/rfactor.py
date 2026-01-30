import mmap
import struct
from providers import GameProvider
from core.telemetry import TelemetryData

class RFactorProvider(GameProvider):
    def __init__(self):
        self.game_name = "rFactor"
        self.map_name = "$rFactorShared$"
        self.mm = None
        print(f"Initialized {self.game_name} Provider")

    def get_telemetry(self) -> TelemetryData:
        if self.mm is None:
            try:
                self.mm = mmap.mmap(-1, 24000, self.map_name) # Open existing
            except FileNotFoundError:
                return TelemetryData(self.game_name, False)
            except Exception:
                return TelemetryData(self.game_name, False)

        try:
            self.mm.seek(0)
            # Struct layout varies by plugin version. 
            # Based on previous bridge.py: Speed @ 236?
            # Let's look for standard ones.
            # Telemetry usually has:
            # float mLastLapTime; // 4
            # float mLastLapTime; // 
            # ...
            # We need to rely on the offsets found in previous file or robust search.
            # Original file said: "Found speed at offset 236"
            
            # Let's try to map generic rFactor1 internal shared memory if using the standard plugin.
            # Check offsets for RPM, Gear, etc.
            # float engineRPM -> offset ?
            # int gear -> offset ?
            
            # For this refactor, I will preserve the Speed reading and add placeholders/guesses for others
            # untill verified. Or assume standard rFactoSharedMemoryMap plugin struct:
            # 
            # byte gear; (offset ~14?)
            # float engineRPM; (offset ~16?)
            # float speed; (offset ~236?? seems far)
            
            # Let's stick strictly to what we know works (Speed @ 236) and try to find others near it?
            # Or just return 0 for others to prevent crashes.
            
            self.mm.seek(236)
            speed_bytes = self.mm.read(4)
            speed_ms = struct.unpack('f', speed_bytes)[0]
            
            # TODO: Improve offset mapping for rFactor
            
            return TelemetryData(
                game_name=self.game_name,
                connected=True,
                speed_kmh=speed_ms * 3.6,
                rpm=0,
                max_rpm=10000,
                gear=0,
                throttle=0,
                brake=0,
                clutch=0
            )
        except Exception as e:
            self.mm.close()
            self.mm = None
            return TelemetryData(self.game_name, False)
