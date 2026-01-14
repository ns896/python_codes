# Author: Nsingh
# Lets listen to the virtial can port and parse the canfd data and log it to a file .

import can
import cantools
import time
import os
import sys
import logging
import logging.handlers
import logging.config
import logging.handlers

from krv_logger.krv_logger import KRV_Logger

log_ = KRV_Logger(name="CANFD_DataParser", file_name="CANFD_DataParser.log", level="INFO")
LOG = log_.get_logger()

LOG.info(">-*--*--*--*-  Jai Guru Dev  -*--*--*--*--*-<")
LOG.info(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
LOG.info("")

# Load the DBC File 
database = cantools.database.load_file('dbc_file/20250404_CANFD_SV_Output_CANDB_ZENDAR_Evaluation_Project_v1.dbc')

# Create a CAN-FD Bus Interface with timeout
LOG.info("Creating CAN-FD bus interface on vcan0...")
bus = can.interface.Bus(channel='vcan0', interface='socketcan', fd=True, timeout=1.0)

LOG.info("Waiting for messages...")
message_count = 0
while True:
    try:
        message = bus.recv(timeout=1.0)
        if message is not None:
            message_count += 1
            LOG.info(f"Message #{message_count} received: ID=0x{message.arbitration_id:X}, DLC={message.dlc}, Data={message.data.hex()}")
            
            # Try to decode the message using the DBC file
            try:
                decoded = database.decode_message(message.arbitration_id, message.data)
                LOG.info(f"Decoded message: {decoded}")
            except Exception as e:
                # Message not in DBC or decode error - that's okay
                pass
        else:
            if message_count == 0:
                LOG.debug("No message received yet...")
    except KeyboardInterrupt:
        LOG.info("Interrupted by user")
        break
    except Exception as e:
        LOG.error(f"Error receiving message: {e}")
        break

LOG.info(f"Total messages received: {message_count}")
bus.shutdown()