import sys
from providers import GameProvider
from core.telemetry import TelemetryData

class IRacingProvider(GameProvider):
    def __init__(self):
        self.game_name = "iRacing"
        try:
            import irsdk
            self.ir = irsdk.IRSDK()
            print("Initialized iRacing Provider")
        except ImportError:
            print("Error: 'pyirsdk' not installed. Run: pip install pyirsdk")
            self.ir = None

    def get_telemetry(self) -> TelemetryData:
        if not self.ir:
             return TelemetryData(self.game_name, False)

        if not self.ir.is_initialized:
            if not self.ir.startup():
                return TelemetryData(self.game_name, False)
        
        self.ir.freeze_var_buffer_latest()
        
        try:
            # Check if connected (in car)
            is_on_track = self.ir['IsOnTrack']
            if not is_on_track:
                 return TelemetryData(self.game_name, True, speed_kmh=0)

            speed_ms = self.ir['Speed']
            rpm = self.ir['RPM']
            gear = self.ir['Gear'] # -1=Reverse, 0=Neutral, 1+=Gears
            throttle = self.ir['Throttle'] # 0-1
            brake = self.ir['Brake'] # 0-1
            clutch = self.ir['Clutch'] # 0-1
            steering = self.ir['SteeringWheelAngle'] # Radians?
            
            # Static data (could be cached)
            max_rpm = self.ir['DriverInfo']['DriverCarSLRedline']
            
            return TelemetryData(
                game_name=self.game_name,
                connected=True,
                speed_kmh=speed_ms * 3.6,
                rpm=rpm,
                max_rpm=max_rpm,
                gear=gear,
                throttle=throttle,
                brake=brake,
                clutch=clutch,
                steering_angle=steering
            )
        except (KeyError, TypeError) as e:
            # print(f"iRacing Data Error: {e}")
            return TelemetryData(self.game_name, True)
