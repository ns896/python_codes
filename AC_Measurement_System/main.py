from tkinter import W
import minimalmodbus
import serial
import time

from krv_comman.TUI.basic_tui import BasicTUI

class ACMeasurementTUI(BasicTUI):
    def __init__(self):
        super().__init__("AC Measurement System")
        

# Configure the serial port for your RS485 converter
# Replace 'COM3' with your actual serial port (e.g., '/dev/ttyUSB0' on Linux)
# The baudrate should match your PZEM-016's configuration (default is usually 9600)
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # Port name, Slave address (1-247)

# Set instrument parameters
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.5  # seconds

# Function to read and process sensor data
def read_pzem_016_data():
    try:
        # Read 9 input registers starting from address 0x0000
        # These registers contain Voltage, Current, Power, Energy, Frequency, Power Factor, and Alarm status
        # Refer to the PZEM-016 manual for register mapping
        data = instrument.read_registers(0x0000, 9, 4) # Register address, number of registers, function code (4 for input registers)

        # Process the raw data according to the PZEM-016 manual
        voltage = data[0] / 10.0
        current = (data[1] + (data[2] << 16)) / 1000.0 # Current is a 32-bit value (two 16-bit registers)
        power = (data[3] + (data[4] << 16)) / 10.0 # Power is a 32-bit value
        energy = (data[5] + (data[6] << 16)) # Energy is a 32-bit value
        frequency = data[7] / 10.0
        power_factor = data[8] / 100.0
        # Alarm status (register 9) can be read separately if needed

        processed_data = {
            "voltage_V": voltage,
            "current_A": current,
            "power_W": power,
            "energy_Wh": energy,
            "frequency_Hz": frequency,
            "power_factor": power_factor,
        }
        return processed_data

    except IOError as e:
        print(f"I/O error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def main():
    app = ACMeasurementTUI()
    app.start()
    # print("Reading PZEM-016 data...")
    # while True:
    #     sensor_data = read_pzem_016_data()
    #     if sensor_data:
    #         print(f"PZEM-016 Data: {sensor_data}")
    #     time.sleep(5) # Read every 5 seconds


if __name__ == "__main__":
    main()