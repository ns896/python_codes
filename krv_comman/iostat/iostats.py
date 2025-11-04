from dataclasses import dataclass
import subprocess
import json
import re 
import time
import asyncio
import datetime

@dataclass
class IOStatData:
    disk_device: str = ""
    r_s: float = 0.0
    w_s: float = 0.0
    d_s: float = 0.0
    f_s: float = 0.0
    rkB_s: float = 0.0
    wkB_s: float = 0.0
    dkB_s: float = 0.0
    rrqm_s: float = 0.0
    wrqm_s: float = 0.0
    drqm_s: float = 0.0
    rrqm: float = 0.0
    wrqm: float = 0.0
    drqm: float = 0.0
    r_await: float = 0.0
    w_await: float = 0.0
    d_await: float = 0.0
    f_await: float = 0.0
    rareq_sz: float = 0.0
    wareq_sz: float = 0.0
    dareq_sz: float = 0.0
    aqu_sz: float = 0.0
    util: float = 0.0
    time_stamp: datetime.datetime = None
    
class IOStats:
    def __init__(self, device_name: str):
        self._device_name = device_name
        self.io_stat_data = IOStatData(disk_device=device_name)
        
    def __str__(self):
        if self.io_stat_data and self.io_stat_data.disk_device:
            return f"IOStats for {self.io_stat_data.disk_device}: {self.io_stat_data.util}% utilization"
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
                    disk_device=disk['disk_device'],
                    r_s=disk.get('r/s', 0.0),
                    w_s=disk.get('w/s', 0.0),
                    d_s=disk.get('d/s', 0.0),
                    f_s=disk.get('f/s', 0.0),
                    rkB_s=disk.get('rkB/s', 0.0),
                    wkB_s=disk.get('wkB/s', 0.0),
                    dkB_s=disk.get('dkB/s', 0.0),
                    rrqm_s=disk.get('rrqm/s', 0.0),
                    wrqm_s=disk.get('wrqm/s', 0.0),
                    drqm_s=disk.get('drqm/s', 0.0),
                    rrqm=disk.get('rrqm', 0.0),
                    wrqm=disk.get('wrqm', 0.0),
                    drqm=disk.get('drqm', 0.0),
                    r_await=disk.get('r_await', 0.0),
                    w_await=disk.get('w_await', 0.0),
                    d_await=disk.get('d_await', 0.0),
                    f_await=disk.get('f_await', 0.0),
                    rareq_sz=disk.get('rareq-sz', 0.0),
                    wareq_sz=disk.get('wareq-sz', 0.0),
                    dareq_sz=disk.get('dareq-sz', 0.0),
                    aqu_sz=disk.get('aqu-sz', 0.0),
                    util=disk.get('util', 0.0),
                    time_stamp=datetime.datetime.now())
        
        print(f"DEBUG: Device '{self._device_name}' not found in current activity, falling back to first entry")
        return None

def main():
    iostat_stats = IOStats("sda")
    
    while True:
        time.sleep(2)
        data = iostat_stats.get_iostat_data()
        if data:
            print(f"Device: {data.disk_device}")
            print(f"Read IOPS: {data.r_s:.2f}")
            print(f"Write IOPS: {data.w_s:.2f}")
            print(f"Read MB/s: {data.rkB_s/1024:.2f}")
            print(f"Write MB/s: {data.wkB_s/1024:.2f}")
            print(f"Utilization: {data.util:.2f}%")
            print(f"Time: {data.time_stamp}")
            # Highlight high utilization
            if data.util > 80:
                print("🚨 HIGH UTILIZATION DETECTED! 🚨")
            print("-" * 40)
        else:
            print("No new data available")

if __name__ == "__main__":
    main()