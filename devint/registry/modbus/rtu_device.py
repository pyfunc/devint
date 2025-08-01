#!/usr/bin/env python3
"""
ModbusRTU Device Implementation for DevInt

This module provides a ModbusRTUDevice class that implements the DevInt
device interface for Modbus RTU devices.
"""

import logging
from typing import Dict, List, Any, Optional

from devint.base.device import BaseDevice
from devint.protocols.modbus_rtu import ModbusRTUProtocol
from devint.protocols.mock_modbus_rtu import MockModbusRTUProtocol

logger = logging.getLogger(__name__)

class ModbusRTUDevice(BaseDevice):
    """
    ModbusRTU Device implementation for DevInt.
    Implements the DevInt device interface for Modbus RTU devices.
    """

    def __init__(self, 
                 device_id: str,
                 name: str = "ModbusRTU Device",
                 unit_id: int = 1,
                 port: str = '/dev/ttyACM0',
                 baudrate: int = None,
                 timeout: float = 1.0,
                 rs485_delay: float = 0.005,
                 enable_state_tracking: bool = True,
                 mock_mode: bool = False):
        """
        Initialize ModbusRTU device.
        
        Args:
            device_id: Unique identifier for this device
            unit_id: Modbus unit ID (slave address)
            port: Serial port to use
            baudrate: Baudrate to use (if None, will use highest prioritized baudrate)
            timeout: Serial timeout in seconds
            rs485_delay: Delay between operations in seconds
            enable_state_tracking: Whether to enable device state tracking
            mock_mode: Whether to use mock mode (no physical hardware required)
        """
        super().__init__(device_id, name)
        
        self.unit_id = unit_id
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.rs485_delay = rs485_delay
        self.enable_state_tracking = enable_state_tracking
        self.mock_mode = mock_mode
        
        # Initialize the ModbusRTU protocol
        if mock_mode:
            logger.info(f"Initializing ModbusRTU device {device_id} in mock mode")
            self.protocol = MockModbusRTUProtocol(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                rs485_delay=rs485_delay,
                enable_state_tracking=enable_state_tracking
            )
        else:
            logger.info(f"Initializing ModbusRTU device {device_id}")
            self.protocol = ModbusRTUProtocol(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                rs485_delay=rs485_delay,
                enable_state_tracking=enable_state_tracking
            )
        
        # Check if connected
        self.connected = self.protocol.is_connected()
        if not self.connected:
            logger.warning(f"Failed to connect to ModbusRTU device {device_id} on {port}")
    
    def initialize(self) -> bool:
        """Initialize the device. Called when the device is added to a service."""
        logger.info(f"Initializing ModbusRTU device {self.device_id}")
        return self.connected
    
    def shutdown(self) -> bool:
        """Shutdown the device. Called when the device is removed from a service."""
        logger.info(f"Shutting down ModbusRTU device {self.device_id}")
        if self.connected:
            self.protocol.disconnect()
            self.connected = False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the device."""
        status = {
            'device_id': self.device_id,
            'device_type': 'ModbusRTU',
            'connected': self.connected,
            'unit_id': self.unit_id,
            'port': self.port,
            'baudrate': self.baudrate,
            'mock_mode': self.mock_mode
        }
        
        if self.connected:
            # Add device state if available
            try:
                device_state = self.protocol.get_device_state(self.unit_id)
                status['device_state'] = device_state
            except Exception as e:
                logger.error(f"Error getting device state: {e}")
        
        return status
    
    def read_coils(self, address: int, count: int) -> List[bool]:
        """Read coil values from the device."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return []
        
        return self.protocol.read_coils(self.unit_id, address, count)
    
    def read_discrete_inputs(self, address: int, count: int) -> List[bool]:
        """Read discrete input values from the device."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return []
        
        return self.protocol.read_discrete_inputs(self.unit_id, address, count)
    
    def read_holding_registers(self, address: int, count: int) -> List[int]:
        """Read holding register values from the device."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return []
        
        return self.protocol.read_holding_registers(self.unit_id, address, count)
    
    def read_input_registers(self, address: int, count: int) -> List[int]:
        """Read input register values from the device."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return []
        
        return self.protocol.read_input_registers(self.unit_id, address, count)
    
    def write_single_coil(self, address: int, value: bool) -> bool:
        """Write a single coil value to the device."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return False
        
        return self.protocol.write_single_coil(self.unit_id, address, value)
    
    def write_single_register(self, address: int, value: int) -> bool:
        """Write a single register value to the device."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return False
        
        return self.protocol.write_single_register(self.unit_id, address, value)
    
    def write_multiple_coils(self, address: int, values: List[bool]) -> bool:
        """Write multiple coil values to the device."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return False
        
        return self.protocol.write_multiple_coils(self.unit_id, address, values)
    
    def write_multiple_registers(self, address: int, values: List[int]) -> bool:
        """Write multiple register values to the device."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return False
        
        return self.protocol.write_multiple_registers(self.unit_id, address, values)
    
    def dump_device_state(self, directory: str = None) -> bool:
        """Dump the device state to a file."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return False
        
        return self.protocol.dump_device_state(self.unit_id, directory)
    
    def auto_detect(self, baudrates: List[int] = None, unit_ids: List[int] = None) -> Dict[str, Any]:
        """Auto-detect Modbus RTU devices."""
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return {'detected': False, 'error': 'Device not connected'}
        
        return self.protocol.auto_detect(baudrates, unit_ids)
    
    def read_register(self, register_name: str) -> Any:
        """Read a register by name.
        
        This implementation maps register names to Modbus addresses and types.
        Format for register_name: 'type_address' where type is one of:
        - coil: for coils (read/write)
        - discrete: for discrete inputs (read-only)
        - holding: for holding registers (read/write)
        - input: for input registers (read-only)
        
        Examples:
        - 'coil_0': Read coil at address 0
        - 'holding_100': Read holding register at address 100
        """
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return None
        
        try:
            # Parse register name to get type and address
            parts = register_name.split('_')
            if len(parts) != 2:
                logger.error(f"Invalid register name format: {register_name}. Expected format: 'type_address'")
                return None
            
            reg_type, address_str = parts
            try:
                address = int(address_str)
                if address < 0:
                    logger.error(f"Negative address not allowed: {register_name}")
                    return None
            except ValueError:
                logger.error(f"Invalid address in register name: {register_name}")
                return None
            
            # Read the appropriate register type
            if reg_type == 'coil':
                result = self.protocol.read_coils(self.unit_id, address, 1)
                return result[0] if result else None
            elif reg_type == 'discrete':
                result = self.protocol.read_discrete_inputs(self.unit_id, address, 1)
                return result[0] if result else None
            elif reg_type == 'holding':
                result = self.protocol.read_holding_registers(self.unit_id, address, 1)
                return result[0] if result else None
            elif reg_type == 'input':
                result = self.protocol.read_input_registers(self.unit_id, address, 1)
                return result[0] if result else None
            else:
                logger.error(f"Unknown register type: {reg_type}")
                return None
        except Exception as e:
            logger.error(f"Error reading register {register_name}: {e}")
            return None
    
    def write_register(self, register_name: str, value: Any) -> bool:
        """Write to a register by name.
        
        This implementation maps register names to Modbus addresses and types.
        Format for register_name: 'type_address' where type is one of:
        - coil: for coils (read/write)
        - holding: for holding registers (read/write)
        
        Examples:
        - 'coil_0': Write to coil at address 0
        - 'holding_100': Write to holding register at address 100
        """
        if not self.connected:
            logger.error(f"Device {self.device_id} not connected")
            return False
        
        try:
            # Parse register name to get type and address
            parts = register_name.split('_')
            if len(parts) != 2:
                logger.error(f"Invalid register name format: {register_name}. Expected format: 'type_address'")
                return False
            
            reg_type, address_str = parts
            try:
                address = int(address_str)
                if address < 0:
                    logger.error(f"Negative address not allowed: {register_name}")
                    return False
            except ValueError:
                logger.error(f"Invalid address in register name: {register_name}")
                return False
            
            # Write to the appropriate register type
            if reg_type == 'coil':
                # Convert value to boolean
                bool_value = bool(value)
                return self.protocol.write_single_coil(self.unit_id, address, bool_value)
            elif reg_type == 'holding':
                # Ensure value is an integer
                try:
                    int_value = int(value)
                    return self.protocol.write_single_register(self.unit_id, address, int_value)
                except (ValueError, TypeError):
                    logger.error(f"Invalid value for holding register: {value}. Must be convertible to int.")
                    return False
            elif reg_type in ['discrete', 'input']:
                logger.error(f"Cannot write to read-only register type: {reg_type}")
                return False
            else:
                logger.error(f"Unknown register type: {reg_type}")
                return False
        except Exception as e:
            logger.error(f"Error writing to register {register_name}: {e}")
            return False
