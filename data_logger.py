
import mmap
import struct
import time
import csv
import datetime
import os

def main():
    map_name = "$rFactorShared$"
    print(f"Waiting for rFactor Shared Memory ({map_name})...")
    
    mm = None
    while mm is None:
        try:
            mm = mmap.mmap(-1, 2048, map_name) # Open 2KB
            print("Connected!")
        except FileNotFoundError:
            time.sleep(1)

    # Setup CSV
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rfactor_telemetry_{timestamp}.csv"
    
    print(f"Logging data to {filename}...")
    print("Press Ctrl+C to stop.")

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header (Offset_0, Offset_4, ...)
        header = ["Time"] + [f"Offset_{i*4}" for i in range(128)]
        writer.writerow(header)

        try:
            while True:
                mm.seek(0)
                data = mm.read(512) # Read first 512 bytes (128 floats)
                
                row = [time.time()]
                for i in range(0, len(data), 4):
                    try:
                        val = struct.unpack('f', data[i:i+4])[0]
                        row.append(val)
                    except:
                        row.append(0)
                
                writer.writerow(row)
                time.sleep(0.05) # 20 Hz
                
        except KeyboardInterrupt:
            print(f"\nStopped. Saved {filename}")
            mm.close()

if __name__ == "__main__":
    main()
