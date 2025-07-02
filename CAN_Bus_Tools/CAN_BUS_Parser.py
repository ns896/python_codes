# Author: Navneet Singh
# CAN_BUS_Parser.py
# Main file for the CAN BUS Parser


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from krv_logger.krv_logger import KRV_Logger
import time
import asyncio
from mobil_eye_structures import Process_Mobil_Eye_CAN_Data, Obstacle_Data_List

# Importing the Data Visualizer
from MobilEye_DataVisualizer import create_and_start_visualizer

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

async def process_can_messages():
    """Separate task for processing CAN messages"""
    global visualizer
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
                    # Add lane data to visualizer
                    if hasattr(mobil_eye_parser, 'left_lane_data') and mobil_eye_parser.left_lane_data.last_update > 0:
                        visualizer.add_lane_data(left_lane_data=mobil_eye_parser.left_lane_data)
                        
                    if hasattr(mobil_eye_parser, 'right_lane_data') and mobil_eye_parser.right_lane_data.last_update > 0:
                        visualizer.add_lane_data(right_lane_data=mobil_eye_parser.right_lane_data)
                        
                    # Add obstacle data to visualizer
                    if hasattr(mobil_eye_parser, 'obstacle_data_list'):
                        visualizer.add_obstacle_data(mobil_eye_parser.obstacle_data_list)
                        
            except Exception as e:
                LOG.error(f"Error decoding message: {e}")
            
            await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            LOG.info("Stopping CAN bus monitoring...")
            break
        except Exception as e:
            LOG.error(f"Bus error: {e}")
            continue

async def visualizer_task():
    """Separate task for running the visualizer"""
    global visualizer
    try:
        # Start the visualizer
        visualizer = await create_and_start_visualizer(host='0.0.0.0', port=8050)
        LOG.info("Visualizer started successfully")
        
        # Keep the visualizer running
        while True:
            await asyncio.sleep(1.0)
            
    except Exception as e:
        LOG.error(f"Visualizer error: {e}")
    finally:
        if visualizer:
            await visualizer.stop_server()

async def main():
    # Create all tasks
    data_logger_task = asyncio.create_task(data_logger(mobil_eye_parser))
    can_processor_task = asyncio.create_task(process_can_messages())
    visualizer_task_obj = asyncio.create_task(visualizer_task())
    
    # Run all tasks concurrently
    try:
        await asyncio.gather(data_logger_task, can_processor_task, visualizer_task_obj)
    except KeyboardInterrupt:
        LOG.info("Shutting down all tasks...")
        # Cancel all tasks gracefully
        data_logger_task.cancel()
        can_processor_task.cancel()
        visualizer_task_obj.cancel()
        
        # Wait for tasks to finish
        await asyncio.gather(
            data_logger_task, 
            can_processor_task, 
            visualizer_task_obj, 
            return_exceptions=True
        )
        
        # Shutdown CAN bus
        bus.shutdown()
        LOG.info("All tasks stopped gracefully")

LOG.info("CAN_BUS_Parser is ending")

if __name__ == "__main__":
    asyncio.run(main())