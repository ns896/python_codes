from re import I
from tkinter import W
import minimalmodbus
import serial
import time
import curses
from dataclasses import dataclass


from krv_comman.TUI.basic_tui import BasicTUI

@dataclass
class ACMeasurementSlaveData:
    voltage: float = 0.0
    current: float = 0.0
    power: float = 0.0
    energy: float = 0.0
    frequency: float = 0.0
    power_factor: float = 0.0
    slave_address: int = 0
@dataclass
class ModBusConfiguration:
    usb_port: str = '/dev/ttyUSB0'
    baudrate: int = 9600
    bytesize: int = 8
    parity: serial.PARITY_NONE = serial.PARITY_NONE
    stopbits: int = 1
    timeout: float = 0.5

class ACMeasurementData:
    def __init__(self, modbus_configuration: ModBusConfiguration):
        self.modbus_configuration = modbus_configuration
        self.instruments = {}  # Dictionary to store instruments by slave address
        self.instrument_data = {}  # Dictionary to store slave data by slave address
        
    def add_slave(self, slave: ACMeasurementSlaveData):
        instrument = minimalmodbus.Instrument(self.modbus_configuration.usb_port, slave.slave_address)
        instrument.serial.baudrate = self.modbus_configuration.baudrate
        instrument.serial.bytesize = self.modbus_configuration.bytesize
        instrument.serial.parity = self.modbus_configuration.parity
        instrument.serial.stopbits = self.modbus_configuration.stopbits
        instrument.serial.timeout = self.modbus_configuration.timeout
        
        # Store instrument and slave data using slave_address as key
        self.instruments[slave.slave_address] = instrument
        self.instrument_data[slave.slave_address] = slave

    def parse_pzem_016_data(self, data: list) -> ACMeasurementSlaveData:
        voltage = data[0] / 10.0
        current = (data[1] + (data[2] << 16)) / 1000.0
        power = (data[3] + (data[4] << 16)) / 10.0
        energy = (data[5] + (data[6] << 16))
        frequency = data[7] / 10.0
        power_factor = data[8] / 100.0
        return ACMeasurementSlaveData(voltage=voltage, current=current, power=power, energy=energy, frequency=frequency, power_factor=power_factor)
    
    def read_data(self):
        if len(self.instruments) == 0:
            return None

        # Read data from all slaves and update their data
        for slave_address, instrument in self.instruments.items():
            try:
                data = instrument.read_registers(0x0000, 9, 4)
                sensor_readings = self.parse_pzem_016_data(data)
                
                slave_data = self.instrument_data[slave_address]
                slave_data.voltage = sensor_readings.voltage
                slave_data.current = sensor_readings.current
                slave_data.power = sensor_readings.power
                slave_data.energy = sensor_readings.energy
                slave_data.frequency = sensor_readings.frequency
                slave_data.power_factor = sensor_readings.power_factor
                
            except Exception as e:
                print(f"Error reading from slave {slave_address}: {e}")
                continue
        
        return self.instrument_data
    
    def get_slave_data(self, slave_address: int) -> ACMeasurementSlaveData:
        """Get data for a specific slave by its address"""
        return self.instrument_data.get(slave_address)
    
    def get_all_slave_addresses(self) -> list:
        """Get list of all slave addresses"""
        return list(self.instrument_data.keys())


class ACMeasurementTUI(BasicTUI):
    def __init__(self, ac_measurement: ACMeasurementData):
        super().__init__("AC Measurement System")
        self.ac_measurement = ac_measurement
        self.last_update = 0
        self.update_interval = 0.05  # 50ms update interval
        self.measurement_data = {}

    def draw_content(self):
        height, width = self.stdscr.getmaxyx()
        self.stdscr.addstr(1, 1, f'Host Time: {time.strftime("%Y-%m-%d %H:%M:%S")}', curses.color_pair(2))
        # Draw measurement data
        y_pos = 4
        if self.measurement_data:
            self.stdscr.addstr(y_pos, 1, "Slave Data:", curses.color_pair(1))
            y_pos += 1
            
            for slave_addr, slave_data in self.measurement_data.items():
                if y_pos >= height - 2:  # Prevent overflow
                    break
                    
                # Format the data nicely
                line = (f"Slave {slave_addr:2d}: "
                       f"V={slave_data.voltage:6.1f}V "
                       f"I={slave_data.current:6.3f}A "
                       f"P={slave_data.power:7.1f}W "
                       f"E={slave_data.energy:8.0f}Wh "
                       f"F={slave_data.frequency:5.1f}Hz "
                       f"PF={slave_data.power_factor:4.2f}")
                
                self.stdscr.addstr(y_pos, 1, line, curses.color_pair(2))
                y_pos += 1
        else:
            self.stdscr.addstr(4, 1, "No measurement data available", curses.color_pair(3))
        
        # Instructions
        if y_pos < height - 2:
            self.stdscr.addstr(height - 2, 1, "Press 'q' to quit, 'r' to refresh", curses.color_pair(4))
    
    def handle_input(self, key):
        """Handle keyboard input"""
        if key == ord('q') or key == ord('Q'):
            self.running = False
        elif key == ord('r') or key == ord('R'):
            # Force immediate refresh
            self.update_measurement_data()
        elif key == curses.KEY_RESIZE:
            self.stdscr.clear()
            self.refresh()

    def update_measurement_data(self):
        """Update measurement data from all slaves"""
        try:
            self.measurement_data = self.ac_measurement.read_data() or {}
        except Exception as e:
            # Handle errors gracefully
            pass

    def run(self):
        """Main loop with periodic data updates"""
        while self.running:
            current_time = time.time()
            
            # Update data at specified intervals
            if current_time - self.last_update >= self.update_interval:
                self.update_measurement_data()
                self.last_update = current_time
            
            self.refresh()
            
            try:
                key = self.stdscr.getch()
                if key != -1:  # -1 means no key pressed
                    self.handle_input(key)
            except curses.error:
                pass  # Ignore curses errors

def main():
    modbus_config = ModBusConfiguration()
    ac_measurement = ACMeasurementData(modbus_config)
    
    # Add slaves
    slave1 = ACMeasurementSlaveData(slave_address=1)
    ac_measurement.add_slave(slave1)
    
    # Start TUI with measurement system
    app = ACMeasurementTUI(ac_measurement)
    app.start() 


if __name__ == "__main__":
    main()