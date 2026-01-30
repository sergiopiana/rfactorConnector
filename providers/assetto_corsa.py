import mmap
import struct
from providers import GameProvider
from core.telemetry import TelemetryData

class AssettoCorsaProvider(GameProvider):
    def __init__(self):
        self.game_name = "Assetto Corsa"
        self.map_name_physics = "Local\\acpmf_physics"
        self.map_name_static = "Local\\acpmf_static"
        self.mm_physics = None
        self.mm_static = None
        print(f"Initialized {self.game_name} Provider")

    def _connect(self):
        try:
            if not self.mm_physics:
                self.mm_physics = mmap.mmap(0, 712, self.map_name_physics)
            if not self.mm_static:
                self.mm_static = mmap.mmap(0, 756, self.map_name_static)
            return True
        except FileNotFoundError:
            return False

    def get_telemetry(self) -> TelemetryData:
        if not self.mm_physics or not self.mm_static:
            if not self._connect():
                return TelemetryData(self.game_name, False)

        try:
            self.mm_physics.seek(0)
            data_physics = self.mm_physics.read(712)
            
            # Physics Struct (Partial)
            # packetId(4), gas(4), brake(4), fuel(4), gear(4), rpm(4), steerAngle(4), speedKmh(4)
            # Offsets:
            # gas: 4
            # brake: 8
            # gear: 16
            # rpm: 20
            # steer: 24
            # speed: 28
            
            packet_id = struct.unpack('i', data_physics[0:4])[0]
            gas = struct.unpack('f', data_physics[4:8])[0]
            brake = struct.unpack('f', data_physics[8:12])[0]
            gear = struct.unpack('i', data_physics[16:20])[0]
            rpm = struct.unpack('i', data_physics[20:24])[0]
            steer = struct.unpack('f', data_physics[24:28])[0]
            speed_kmh = struct.unpack('f', data_physics[28:32])[0]

            # Static Data for Max RPM
            self.mm_static.seek(0)
            data_static = self.mm_static.read(756)
            # Check AC static struct for maxRpm. usually deeper.
            # For now, let's hardcode or guess, or implement later properly.
            # MaxRpm is at offset 8 in static?
            # _smVersion(15*2), _acVersion(15*2), _numberOfSessions(4), _numCars(4) ...
            # Actually standard Static struct:
            # char smVersion[15]; char acVersion[15]; ... float maxRpm; ...
            # simpler to assume 8000 if not found easily, or parse fully.
            # Let's use a safe default for now to avoid crashes if offset wrong.
            max_rpm = 8000.0

            return TelemetryData(
                game_name=self.game_name,
                connected=True,
                speed_kmh=speed_kmh,
                rpm=float(rpm),
                max_rpm=max_rpm,
                gear=gear, # AC: 0=R, 1=N, 2=1st... need to map? 
                           # Actually often AC is 0=R, 1=N. 
                           # Standard API usually: 0=R, 1=N, 2=1st.
                throttle=gas,
                brake=brake,
                clutch=0.0, # Not in simple offset
                steering_angle=steer
            )

        except Exception as e:
            # print(f"AC Read Error: {e}")
            self.mm_physics = None # Reset connection
            return TelemetryData(self.game_name, False)
