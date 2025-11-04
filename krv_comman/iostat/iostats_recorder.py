"""
Author: Navneet Singh
iostats_recorder.py
This script records the iostat data to a file

input : sda or whatever is the disk name is passed as an argument
output file format: hdf5

"""

import h5py
import numpy as np
import datetime
import time
import argparse
import sys
from iostats import IOStatData, IOStats


class IOStatsRecorder:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file = None
        self.dataset = None
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialize or open the HDF5 file and create/access the dataset"""
        self.file = h5py.File(self.file_path, 'a')  # 'a' mode for append
        
        # Define the structured dtype for all fields
        dtype = [
            ('disk_device', 'S16'),  # Fixed-length string (16 chars)
            ('r_s', np.float64),
            ('w_s', np.float64),
            ('d_s', np.float64),
            ('f_s', np.float64),
            ('rkB_s', np.float64),
            ('wkB_s', np.float64),
            ('dkB_s', np.float64),
            ('rrqm_s', np.float64),
            ('wrqm_s', np.float64),
            ('drqm_s', np.float64),
            ('rrqm', np.float64),
            ('wrqm', np.float64),
            ('drqm', np.float64),
            ('r_await', np.float64),
            ('w_await', np.float64),
            ('d_await', np.float64),
            ('f_await', np.float64),
            ('rareq_sz', np.float64),
            ('wareq_sz', np.float64),
            ('dareq_sz', np.float64),
            ('aqu_sz', np.float64),
            ('util', np.float64),
            ('time_stamp_unix', np.float64),  # Unix timestamp
            ('time_stamp_iso', 'S32'),  # ISO format string
        ]
        
        dataset_name = 'iostat_data'
        
        if dataset_name not in self.file:
            # Create new dataset with initial size and maxshape for unlimited growth
            self.dataset = self.file.create_dataset(
                dataset_name,
                shape=(0,),
                maxshape=(None,),
                dtype=dtype,
                chunks=True,  # Enable chunking for better performance
                compression='gzip'  # Compress data to save space
            )
            # Store metadata
            self.file.attrs['created'] = datetime.datetime.now().isoformat()
            self.file.attrs['description'] = 'IOStat data recording'
        else:
            # Access existing dataset
            self.dataset = self.file[dataset_name]
    
    def record(self, data: IOStatData):
        """Append a single IOStatData record to the dataset"""
        if self.dataset is None:
            raise RuntimeError("Dataset not initialized. Call _initialize_file() first.")
        
        # Convert timestamp to Unix timestamp and ISO string
        if data.time_stamp:
            timestamp_unix = data.time_stamp.timestamp()
            timestamp_iso = data.time_stamp.isoformat().encode('utf-8')
        else:
            timestamp_unix = 0.0
            timestamp_iso = b''
        
        # Create a numpy array with the record
        record = np.array([(
            data.disk_device.encode('utf-8') if data.disk_device else b'',
            float(data.r_s),
            float(data.w_s),
            float(data.d_s),
            float(data.f_s),
            float(data.rkB_s),
            float(data.wkB_s),
            float(data.dkB_s),
            float(data.rrqm_s),
            float(data.wrqm_s),
            float(data.drqm_s),
            float(data.rrqm),
            float(data.wrqm),
            float(data.drqm),
            float(data.r_await),
            float(data.w_await),
            float(data.d_await),
            float(data.f_await),
            float(data.rareq_sz),
            float(data.wareq_sz),
            float(data.dareq_sz),
            float(data.aqu_sz),
            float(data.util),
            float(timestamp_unix),
            timestamp_iso
        )], dtype=self.dataset.dtype)
        
        # Resize dataset to accommodate new record
        current_size = self.dataset.shape[0]
        self.dataset.resize((current_size + 1,))
        
        # Append the record
        self.dataset[current_size] = record[0]
        
        # Flush to ensure data is written
        self.file.flush()
    
    def close(self):
        """Close the HDF5 file"""
        if self.file:
            self.file.close()
            self.file = None
            self.dataset = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Destructor to ensure file is closed"""
        self.close()


def main():
    """Main function to record iostat data to HDF5 file"""
    parser = argparse.ArgumentParser(
        description='Record iostat data to HDF5 file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
                Examples:
                python iostats_recorder.py sda output.h5
                python iostats_recorder.py sda output.h5 --interval 5
                python iostats_recorder.py sda output.h5 --interval 2 --count 100
                """
        )
    parser.add_argument('device', help='Disk device name (e.g., sda, nvme0n1)')
    parser.add_argument('output_file', help='Output HDF5 file path')
    parser.add_argument('--interval', type=float, default=2.0,
                        help='Sampling interval in seconds (default: 2.0)')
    parser.add_argument('--count', type=int, default=None,
                        help='Number of samples to record (default: infinite)')
    
    args = parser.parse_args()
    
    print(f"Starting IOStat recorder")
    print(f"Device: {args.device}")
    print(f"Output file: {args.output_file}")
    print(f"Interval: {args.interval} seconds")
    if args.count:
        print(f"Count: {args.count} samples")
    else:
        print("Count: Infinite (press Ctrl+C to stop)")
    print("-" * 60)
    
    sample_count = 0
    try:
        # Create recorder and IOStats instances
        with IOStatsRecorder(args.output_file) as recorder:
            iostat_stats = IOStats(args.device)
            while True:
                # Check if we've reached the count limit
                if args.count and sample_count >= args.count:
                    print(f"\nRecorded {sample_count} samples. Stopping.")
                    break
                
                # Get iostat data
                data = iostat_stats.get_iostat_data()
                
                if data:
                    # Record the data
                    recorder.record(data)
                    sample_count += 1
                    
                    # Print status
                    print(f"[Sample {sample_count}] Device: {data.disk_device} | "
                          f"Read IOPS: {data.r_s:.2f} | Write IOPS: {data.w_s:.2f} | "
                          f"Util: {data.util:.2f}% | Time: {data.time_stamp}")
                
                else:
                    print("  Warning: No data available")
                
                # Wait before next sample
                time.sleep(args.interval)
                
    except KeyboardInterrupt:
        print(f"\n\nRecording interrupted by user.")
        print(f"Total samples recorded: {sample_count}")
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()