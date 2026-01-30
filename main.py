import argparse
import time
import json
import sys
from interfaces.websocket_server import WebSocketServer
from core.telemetry import TelemetryData

# Provider Imports
from providers.test_provider import TestProvider
from providers.iracing import IRacingProvider
from providers.assetto_corsa import AssettoCorsaProvider
from providers.rfactor import RFactorProvider
from providers.beamng import BeamNGProvider

def main():
    parser = argparse.ArgumentParser(description="SimRacing Universal Connector")
    parser.add_argument("--game", required=True, help="Game to connect to (iracing, ac, rfactor, beamng, test)")
    parser.add_argument("--fps", type=int, default=60, help="Target update rate (FPS)")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket Port")
    
    args = parser.parse_args()
    
    # Initialize Provider
    provider = None
    if args.game == 'test':
        provider = TestProvider()
    elif args.game == 'iracing':
        provider = IRacingProvider()
        # print("iRacing implementation pending migration.")
        # sys.exit(1)
    elif args.game == 'ac':
        provider = AssettoCorsaProvider()
        # print("Assetto Corsa implementation pending migration.")
        # sys.exit(1)
    elif args.game == 'rfactor':
        provider = RFactorProvider()
        # print("rFactor implementation pending migration.")
        # sys.exit(1)
    elif args.game == 'beamng':
        provider = BeamNGProvider()
        # print("BeamNG implementation pending migration.")
        # sys.exit(1)
    else:
        print(f"Unknown game: {args.game}")
        sys.exit(1)
        
    # Start Server
    server = WebSocketServer(port=args.port)
    server.start_server()
    
    print(f"Connector started for {args.game}. Broadcasting on port {args.port}...")
    
    # Main Loop
    interval = 1.0 / args.fps
    
    try:
        while True:
            start_time = time.time()
            
            # 1. Get Telemetry
            telemetry: TelemetryData = provider.get_telemetry()
            
            # 2. Broadcast
            server.broadcast(telemetry.to_dict())
            
            # 3. Print stats (optional, for debug)
            if telemetry.connected:
                print(f"Connected: {telemetry.game_name} | Speed: {telemetry.speed_kmh:.1f} km/h | RPM: {telemetry.rpm:.0f}", end='\r')
            else:
                print(f"Waiting for {args.game}...", end='\r')
            
            # Timing
            elapsed = time.time() - start_time
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\nStopping...")

if __name__ == "__main__":
    main()
