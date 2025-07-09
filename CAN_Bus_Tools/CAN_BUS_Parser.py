# Author: Navneet Singh
# CAN_BUS_Parser.py
# Main file for the CAN BUS Parser


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from krv_logger.krv_logger import KRV_Logger
import time
import asyncio
import threading

from mobil_eye_structures import Process_Mobil_Eye_CAN_Data, Obstacle_Data_List

# Importing the Data Visualizer
from MobilEye_DataVisualizer import MobilEyeVisualizer

# Importing CAN Related Libraries
import can
import cantools

log_ = KRV_Logger(name="CAN_BUS_Parser", file_name="CAN_BUS_Parser.log", level="INFO")
LOG = log_.get_logger()

LOG.info(">-*--*--*--*-  Jai Guru Dev  -*--*--*--*--*-<")
LOG.info(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
LOG.info("")

# Load the DBC File 
database = cantools.database.load_file('dbc_files/Zendar_Private_CAN.dbc')

# Create a CAN Bus Interface with timeout
LOG.info("Creating CAN bus interface on vcan0...")
bus = can.interface.Bus(channel='vcan0', interface='socketcan', timeout=1.0)

LOG.info("Waiting for CAN messages...")
message_count = 0

# Object that will store all the obstacle data
obstacle_data_list = Obstacle_Data_List()
mobil_eye_parser = Process_Mobil_Eye_CAN_Data(database)

# Global visualizer instance
visualizer = None
visualizer_thread = None

def start_visualizer_thread():
    """Start the visualizer in a separate thread"""
    global visualizer
    try:
        # Create and start the visualizer
        visualizer = MobilEyeVisualizer(host='0.0.0.0', port=8050)
        
        # Start the Dash server in the current thread
        visualizer.app.run(
            host=visualizer.host,
            port=visualizer.port,
            debug=False,
            use_reloader=False
        )
        
    except Exception as e:
        LOG.error(f"Visualizer thread error: {e}")

async def data_logger(mobil_eye_parser):
    """Separate task for data logging"""
    while True:
        try:
            LOG.info(f"Obstacle Data: {mobil_eye_parser.obstacle_data_list}")
            LOG.info(f"Right Lane Data: {mobil_eye_parser.right_lane_data}")
            LOG.info(f"Left Lane Data: {mobil_eye_parser.left_lane_data}")
            await asyncio.sleep(1.0)  # Log every second
        except Exception as e:
            LOG.error(f"Data logger error: {e}")
            await asyncio.sleep(1.0)

def process_can_messages():
    """Separate thread for processing CAN messages"""
    global visualizer
    LOG.info("CAN message processing thread started")
    
    while True:
        try:
            msg = bus.recv(timeout=1.0)
            if msg is None:
                LOG.warning("No message received in 1 second timeout")
                continue
            
            try:
                mobil_eye_parser.parse_mobil_eye_can_data(msg, obstacle_data_list)
                
                # Add data to visualizer if available
                if visualizer:
                    # Add lane data to visualizer - combine both lanes in single call
                    left_lane = mobil_eye_parser.left_lane_data if hasattr(mobil_eye_parser, 'left_lane_data') and mobil_eye_parser.left_lane_data.last_update > 0 else None
                    right_lane = mobil_eye_parser.right_lane_data if hasattr(mobil_eye_parser, 'right_lane_data') and mobil_eye_parser.right_lane_data.last_update > 0 else None
                    
                    if left_lane or right_lane:
                        visualizer.add_lane_data(left_lane_data=left_lane, right_lane_data=right_lane)
                        
                    # Add obstacle data to visualizer
                    if hasattr(mobil_eye_parser, 'obstacle_data_list'):
                        visualizer.add_obstacle_data(mobil_eye_parser.obstacle_data_list)
                        
            except Exception as e:
                LOG.error(f"Error decoding message: {e}")
            
            time.sleep(0.001)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            LOG.info("Stopping CAN bus monitoring...")
            break
        except Exception as e:
            LOG.error(f"Bus error: {e}")
            continue
    
    LOG.info("CAN message processing thread stopped")

async def main():
    global visualizer_thread
    
    # Start visualizer in a separate thread
    LOG.info("Starting visualizer in separate thread...")
    visualizer_thread = threading.Thread(target=start_visualizer_thread, daemon=True)
    visualizer_thread.start()
    
    # Wait a moment for visualizer to start
    await asyncio.sleep(3)
    
    # Start CAN processing in a separate thread
    LOG.info("Starting CAN message processing thread...")
    can_processor_thread = threading.Thread(target=process_can_messages, daemon=True)
    can_processor_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        LOG.info("Shutting down all threads...")
        
        # Shutdown CAN bus
        bus.shutdown()
        LOG.info("All threads stopped gracefully")

LOG.info("CAN_BUS_Parser is ending")

if __name__ == "__main__":
    asyncio.run(main())