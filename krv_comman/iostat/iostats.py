from dataclasses import dataclass
import subprocess
import json
import re 
import time
import asyncio
import datetime

@dataclass
class IOStatData:
    device_name: str = ""
    read_requests_per_second: float = 0.0
    write_requests_per_second: float = 0.0
    kb_data_read_per_second: float = 0.0
    kb_data_write_per_second: float = 0.0
    read_req_merged_persec: float = 0.0
    write_req_merged_persec: float = 0.0
    read_time_wait_latency: float = 0.0
    write_time_wait_latency: float = 0.0
    device_utilization: float = 0.0
    time_stamp: datetime.datetime = None
    
class IOStats:
    def __init__(self, device_name: str):
        self._device_name = device_name
        self.io_stat_data = IOStatData(device_name=device_name)
        
    def __str__(self):
        if self.io_stat_data and self.io_stat_data.device_name:
            return f"IOStats for {self.io_stat_data.device_name}: {self.io_stat_data.device_utilization}% utilization"
        return f"IOStats for {self._device_name}: No data available"

    def get_iostat_data(self) -> IOStatData:
        """Get current iostat data by running iostat with 1-second interval"""
        try:
            # Use 1 2 to get 2 samples: first is average since boot, second is current activity
            result = subprocess.run(["iostat", "-x", "-p", self._device_name, "-o", "JSON", "1", "2"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.iostat_data_raw = json.loads(result.stdout)
                self.io_stat_data = self._parse_iostat_data(self.iostat_data_raw)
                return self.io_stat_data
            else:
                print(f"iostat error: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error getting iostat data: {e}")
            return None

    def _parse_iostat_data(self, data: dict) -> IOStatData:
        """
        Parse the JSON data from iostat and return the IOStatData object
        This function assumes that command is run with 2 samples, first sample is average since boot, second sample is current activity
        """
        # Get the statistics entries
        statistics = data['sysstat']['hosts'][0]['statistics']
        print(f"DEBUG: Found {len(statistics)} statistics entries")
        
        # Print all entries with full details
        for i, stat in enumerate(statistics):
            print(f"DEBUG: Entry {i} has {len(stat['disk'])} devices")
            for disk in stat['disk']:
                if disk['disk_device'] == self._device_name:
                    print(f"DEBUG: Entry {i}: util={disk['util']}%, w/s={disk['w/s']}, r/s={disk['r/s']}")
                else:
                    print(f"DEBUG: Entry {i}: Other device {disk['disk_device']} with util={disk['util']}%")
        
        # Use the SECOND entry (index 1) which contains current activity
        # First entry (index 0) is average since boot, second entry is current
        if len(statistics) >= 2:
            current_stat = statistics[1] 
            print(f"DEBUG: Using entry 1 (current activity)")
        else:
            current_stat = statistics[-1]  # Fallback to last entry if only one
            print(f"DEBUG: Using entry {len(statistics)-1} (fallback)")
        
        for disk in current_stat['disk']:
            if disk['disk_device'] == self._device_name:
                print(f"DEBUG: Found device! Using current activity with util={disk['util']}%")
                return IOStatData(
                    device_name=disk['disk_device'],
                    read_requests_per_second=disk['r/s'],
                    write_requests_per_second=disk['w/s'],
                    kb_data_read_per_second=disk['rkB/s'],
                    kb_data_write_per_second=disk['wkB/s'],
                    read_req_merged_persec=disk['rrqm/s'],
                    write_req_merged_persec=disk['wrqm/s'],
                    read_time_wait_latency=disk['r_await'],
                    write_time_wait_latency=disk['w_await'],
                    device_utilization=disk['util'],
                    time_stamp=datetime.datetime.now())
        
        print(f"DEBUG: Device '{self._device_name}' not found in current activity, falling back to first entry")
        return None

def main():
    iostat_stats = IOStats("sda")
    
    while True:
        time.sleep(2)
        data = iostat_stats.get_iostat_data()
        if data:
            print(f"Device: {data.device_name}")
            print(f"Read IOPS: {data.read_requests_per_second:.2f}")
            print(f"Write IOPS: {data.write_requests_per_second:.2f}")
            print(f"Read MB/s: {data.kb_data_read_per_second/1024:.2f}")
            print(f"Write MB/s: {data.kb_data_write_per_second/1024:.2f}")
            print(f"Utilization: {data.device_utilization:.2f}%")
            print(f"Time: {data.time_stamp}")
            # Highlight high utilization
            if data.device_utilization > 80:
                print("🚨 HIGH UTILIZATION DETECTED! 🚨")
            print("-" * 40)
        else:
            print("No new data available")

if __name__ == "__main__":
    main()