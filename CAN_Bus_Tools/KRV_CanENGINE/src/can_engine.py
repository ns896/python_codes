"""
KRV CAN Engine

KRV_CanEngine is a class that provides a simple interface for receiving CAN messages and decoding them using a DBC file.

Attributes:
    dbc_file: str
    can_port: str
    message_count: int
    can_receiver: can.interface.Bus
    database: cantools.database.Database

Methods:
    next(self, timeout_value: float = 1.0) -> dict | None:
        Receives a CAN message and returns a dictionary with the message information and decoded data.
"""

import os
import cantools
import can
import subprocess

class KRV_CanEngine:
    def __init__(self, dbc_file: str, can_port: str):
        self.dbc_file = dbc_file
        self.can_port = can_port
        self.message_count = 0
        
        if not self.verify_input_arguments():
            raise ValueError("Invalid input arguments")
        
        # Constructor for the CAN receiver
        self.can_receiver = self.can_receiver_constructor()
        self.database = self.load_dbc_file()

    def verify_input_arguments(self) -> bool:
        if not os.path.isfile(self.dbc_file):
            raise FileNotFoundError(f"DBC file not found: {self.dbc_file}")
        if not self.dbc_file.endswith('.dbc'):
            raise ValueError("DBC file must have .dbc extension")
        
        # Verifying CAN port related arguments
        if not self.can_port:
            raise ValueError("CAN port is required")
        # Verify if can0, vcan0 even exist
        self.verify_can_port_exists(self.can_port)

        return True

    def verify_can_port_exists(self, can_port: str) -> None:
        """
        Verify that a CAN port exists and is available.
        
        Args:
            can_port: Name of the CAN port to verify (e.g., 'can0', 'vcan0')
            
        Raises:
            ValueError: If the port doesn't exist or is not UP
        """
        # Check if port exists by checking /sys/class/net/ (most reliable)
        net_interface_path = f"/sys/class/net/{can_port}"
        if not os.path.exists(net_interface_path):
            # Fallback: use 'ip link show' command
            try:
                result = subprocess.run(
                    ['ip', 'link', 'show', can_port],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode != 0:
                    raise ValueError(f"CAN port '{can_port}' does not exist")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                raise ValueError(f"CAN port '{can_port}' does not exist")
        
        # Check if port is UP using 'ip link show'
        try:
            result = subprocess.run(
                ['ip', 'link', 'show', can_port],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                output = result.stdout
                # Check if port is in DOWN state
                if 'state DOWN' in output and 'state UP' not in output:
                    raise ValueError(f"CAN port '{can_port}' exists but is DOWN. Bring it up with: sudo ip link set {can_port} up")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # If we can't check state, at least verify it exists via sysfs
            pass

    def next(self, timeout_value: float = 1.0) -> dict | None:
        message = self.can_receiver.recv(timeout=timeout_value)
        if message is not None:
            self.message_count += 1
            
            # Try to decode the message using the DBC file
            try:
                decoded = self.database.decode_message(message.arbitration_id, message.data)
                return {
                    'message_id': message.arbitration_id,
                    'dlc': message.dlc,
                    'data': message.data.hex(),
                    'decoded': decoded,
                    'count': self.message_count
                }
            except Exception as e:
                # Message not in DBC or decode error - return raw message info
                return {
                    'message_id': message.arbitration_id,
                    'dlc': message.dlc,
                    'data': message.data.hex(),
                    'decoded': None,
                    'error': str(e),
                    'count': self.message_count
                }
        else:
            return None

    def load_dbc_file(self):
        self.database = cantools.database.load_file(self.dbc_file)
        return self.database

    def can_receiver_constructor(self):
        self.can_receiver = can.interface.Bus(channel=self.can_port, interface='socketcan', timeout=1.0)
        return self.can_receiver    

    def can_receiver_destructor(self):
        self.can_receiver.shutdown()
        return True
