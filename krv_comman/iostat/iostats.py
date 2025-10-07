import subprocess
import json
import re 
import time
import asyncio



class IOStats:
    def __init__(self, device_name: str):
        self._device_name = device_name
        self.iostat_data = {}

    def get_iostat_data(self) -> dict:
        """Get current iostat data by running iostat once"""
        try:
            # Run iostat once to get current snapshot
            result = subprocess.run(["iostat", "-xz", "-p", self._device_name, "-o", "JSON"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.iostat_data = json.loads(result.stdout)
                return self.iostat_data
            else:
                print(f"iostat error: {result.stderr}")
                return {}
        except Exception as e:
            print(f"Error getting iostat data: {e}")
            return {}


def main():
    iostat_stats = IOStats("nvme0n1")
    print("Initial data:")
    print(iostat_stats)
    
    while True:
        time.sleep(1)
        data = iostat_stats.get_iostat_data()
        if data:
            print(json.dumps(data, indent=2))
        else:
            print("No new data available")

if __name__ == "__main__":
    main()