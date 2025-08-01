#!/usr/bin/env python3
"""
Modbus RTU Protocol Implementation for DevInt

This module provides a wrapper around the modapi.rtu.base.ModbusRTU class
to integrate it with the DevInt unified device interface framework.
"""

import logging
import os
import sys
from typing import Dict, List, Any

# Add modapi to path if not installed
modapi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../modapi'))
if os.path.exists(modapi_path) and modapi_path not in sys.path:
    sys.path.append(modapi_path)

try:
    from modapi.rtu.base import ModbusRTU as ModapiModbusRTU
    from modapi.rtu.device_state import device_manager
    # Import other modules as needed
except ImportError:
    raise ImportError(
        "Could not import modapi. Make sure it's installed or available at '../../../modapi'"
    )

logger = logging.getLogger(__name__)

class ModbusRTUProtocol:
    """
    ModbusRTU Protocol implementation for DevInt.
    Wraps the modapi.rtu.base.ModbusRTU class to provide a unified interface.
    """

    def __init__(self, 
                 port: str = '/dev/ttyACM0',
                 baudrate: int = None,
                 timeout: float = 1.0,
                 rs485_delay: float = 0.005,
                 enable_state_tracking: bool = True):
        """
        Initialize ModbusRTU protocol.
        
        Args:
            port: Serial port to use
            baudrate: Baudrate to use (if None, will use highest prioritized baudrate)
            timeout: Serial timeout in seconds
            rs485_delay: Delay between operations in seconds
            enable_state_tracking: Whether to enable device state tracking
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.rs485_delay = rs485_delay
        self.enable_state_tracking = enable_state_tracking
        
        # Initialize the ModbusRTU instance from modapi
        self.rtu = ModapiModbusRTU(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            rs485_delay=rs485_delay,
            enable_state_tracking=enable_state_tracking
        )
        
        # Connect to the device
        self.connected = self.rtu.connect()
        if not self.connected:
            logger.warning(f"Failed to connect to ModbusRTU device on {port}")
    
    def is_connected(self) -> bool:
        """Check if the device is connected."""
        return self.connected
    
    def disconnect(self) -> bool:
        """Disconnect from the device."""
        if self.connected:
            self.rtu.disconnect()
            self.connected = False
        return True
    
    def read_coils(self, unit_id: int, address: int, count: int) -> List[bool]:
        """Read coil values from the device."""
        try:
            return self.rtu.read_coils(unit_id, address, count)
        except Exception as e:
            logger.error(f"Error reading coils: {e}")
            return []
    
    def read_discrete_inputs(self, unit_id: int, address: int, count: int) -> List[bool]:
        """Read discrete input values from the device."""
        try:
            return self.rtu.read_discrete_inputs(unit_id, address, count)
        except Exception as e:
            logger.error(f"Error reading discrete inputs: {e}")
            return []
    
    def read_holding_registers(self, unit_id: int, address: int, count: int) -> List[int]:
        """Read holding register values from the device."""
        try:
            return self.rtu.read_holding_registers(unit_id, address, count)
        except Exception as e:
            logger.error(f"Error reading holding registers: {e}")
            return []
    
    def read_input_registers(self, unit_id: int, address: int, count: int) -> List[int]:
        """Read input register values from the device."""
        try:
            return self.rtu.read_input_registers(unit_id, address, count)
        except Exception as e:
            logger.error(f"Error reading input registers: {e}")
            return []
    
    def write_single_coil(self, unit_id: int, address: int, value: bool) -> bool:
        """Write a single coil value to the device."""
        try:
            return self.rtu.write_single_coil(unit_id, address, value)
        except Exception as e:
            logger.error(f"Error writing single coil: {e}")
            return False
    
    def write_single_register(self, unit_id: int, address: int, value: int) -> bool:
        """Write a single register value to the device."""
        try:
            return self.rtu.write_single_register(unit_id, address, value)
        except Exception as e:
            logger.error(f"Error writing single register: {e}")
            return False
    
    def write_multiple_coils(self, unit_id: int, address: int, values: List[bool]) -> bool:
        """Write multiple coil values to the device."""
        try:
            return self.rtu.write_multiple_coils(unit_id, address, values)
        except Exception as e:
            logger.error(f"Error writing multiple coils: {e}")
            return False
    
    def write_multiple_registers(self, unit_id: int, address: int, values: List[int]) -> bool:
        """Write multiple register values to the device."""
        try:
            return self.rtu.write_multiple_registers(unit_id, address, values)
        except Exception as e:
            logger.error(f"Error writing multiple registers: {e}")
            return False
    
    def get_device_state(self, unit_id: int) -> Dict[str, Any]:
        """Get the current state of the device."""
        try:
            # Get device state using device manager
            device_state = device_manager.get_device(self.port, unit_id)
            if device_state:
                from dataclasses import asdict
                return asdict(device_state)
            return {}
        except Exception as e:
            logger.error(f"Error getting device state: {e}")
            return {}
    
    def dump_device_state(self, unit_id: int, directory: str = None) -> bool:
        """Dump the device state to a file."""
        try:
            if directory is None:
                directory = os.path.join(os.path.expanduser("~"), ".modbus_logs")
            device_manager.dump_device(self.port, unit_id, directory)
            return True
        except Exception as e:
            logger.error(f"Error dumping device state: {e}")
            return False
    
    def auto_detect(self, baudrates: List[int] = None, unit_ids: List[int] = None) -> Dict[str, Any]:
        """Auto-detect Modbus RTU devices."""
        try:
            # Use modapi's auto-detection functionality if available
            if hasattr(self.rtu, 'auto_detect'):
                return self.rtu.auto_detect(baudrates, unit_ids)
            
            # Otherwise implement basic detection
            result = {
                'detected': False,
                'unit_id': None,
                'baudrate': None,
                'function_code': None
            }
            
            if baudrates is None:
                baudrates = [9600, 19200, 38400, 57600, 115200]
            
            if unit_ids is None:
                unit_ids = [1, 2, 3, 10, 0xFF]  # Common unit IDs
            
            # Try different combinations
            for baudrate in baudrates:
                self.rtu.baudrate = baudrate
                self.rtu.disconnect()
                if self.rtu.connect():
                    for unit_id in unit_ids:
                        # Try reading holding registers (most common)
                        try:
                            if self.rtu.read_holding_registers(unit_id, 0, 1):
                                result['detected'] = True
                                result['unit_id'] = unit_id
                                result['baudrate'] = baudrate
                                result['function_code'] = 3  # Read holding registers
                                return result
                        except Exception:
                            pass
                        
                        # Try reading coils
                        try:
                            if self.rtu.read_coils(unit_id, 0, 1):
                                result['detected'] = True
                                result['unit_id'] = unit_id
                                result['baudrate'] = baudrate
                                result['function_code'] = 1  # Read coils
                                return result
                        except Exception:
                            pass
            
            return result
        except Exception as e:
            logger.error(f"Error in auto-detection: {e}")
            return {'detected': False, 'error': str(e)}
