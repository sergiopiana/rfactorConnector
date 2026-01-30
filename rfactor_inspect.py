import mmap
import struct
import time
import os

def main():
    map_name = "$rFactorShared$"
    # Try different map names if this fails? 
    # rF1 MapPlugin usually uses $rFactorShared$
    
    print(f"Attempting to open Shared Memory: {map_name}")
    print("Please make sure rFactor is running and in a race/practice session.")
    print("Also ensure you have the 'MapPlugin' or 'rFactorSharedMemoryMap' plugin installed.")
    
    try:
        # Open mmap
        # Size approx 24KB is common for these plugins
        try:
            mm = mmap.mmap(-1, 1024, "$rFactorShared$")
            print(f"Connected to $rFactorShared$")
        except FileNotFoundError:
            print("Could not find $rFactorShared$, trying rFactor 2 name...")
            map_name = "$rFactor2Shared$"
            mm = mmap.mmap(-1, 1024, map_name)
            print(f"Connected to {map_name}!") 
        except FileNotFoundError:
            print(f"Could not find {map_name}, trying Iron Wolf Telemetry...")
            map_name = "$rFactor2SMMP_Telemetry$"
            mm = mmap.mmap(-1, 1024, map_name)
            print(f"Connected to {map_name}!") 
        
        print("Connected! Reading first 64 floats...")
        print("Drive the car to see which values change and look like Speed (m/s).")
        
        while True:
            mm.seek(0)
            data = mm.read(256) # Read first 256 bytes (64 floats)
            
            floats = []
            for i in range(0, len(data), 4):
                val = struct.unpack('f', data[i:i+4])[0]
                floats.append(val)
                
            # Clear screen (hacky)
            # print("\033[H\033[J", end="") 
            print("-" * 50)
            for i, val in enumerate(floats):
                print(f"Offset {i*4}: {val:.3f}", end="\t")
                if (i+1) % 4 == 0:
                    print()
            
            # Heuristic for speed:
            # Usually offset 20 or similar.
            # Convert m/s to km/h (~ * 3.6)
            
            time.sleep(0.5)
            
    except FileNotFoundError:
        print(f"Could not find Shared Memory: {map_name}")
        print("1. Is rFactor running?")
        print("2. Is the Shared Memory Plugin installed?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
