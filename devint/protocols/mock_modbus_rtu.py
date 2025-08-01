#!/usr/bin/env python3
"""
Mock Modbus RTU Protocol Implementation for DevInt

This module provides a mock implementation of the ModbusRTU protocol
for testing purposes without requiring physical hardware.
"""

import logging
import random
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class MockModbusRTUProtocol:
    """
    Mock ModbusRTU Protocol implementation for DevInt.
    Simulates a Modbus RTU device for testing without physical hardware.
    """

    def __init__(self, 
                 port: str = '/dev/ttyACM0',
                 baudrate: int = None,
                 timeout: float = 1.0,
                 rs485_delay: float = 0.005,
                 enable_state_tracking: bool = True):
        """
        Initialize Mock ModbusRTU protocol.
        
        Args:
            port: Serial port to use (ignored in mock)
            baudrate: Baudrate to use (ignored in mock)
            timeout: Serial timeout in seconds (ignored in mock)
            rs485_delay: Delay between operations in seconds (ignored in mock)
            enable_state_tracking: Whether to enable device state tracking
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.rs485_delay = rs485_delay
        self.enable_state_tracking = enable_state_tracking
        
        # Always connected in mock mode
        self.connected = True
        
        # Mock device state
        self.mock_state = {
            'coils': {i: bool(random.randint(0, 1)) for i in range(100)},
            'discrete_inputs': {i: bool(random.randint(0, 1)) for i in range(100)},
            'holding_registers': {i: random.randint(0, 65535) for i in range(100)},
            'input_registers': {i: random.randint(0, 65535) for i in range(100)},
        }
        
        logger.info(f"Initialized Mock ModbusRTU on {port} (simulated)")
    
    def is_connected(self) -> bool:
        """Check if the device is connected."""
        return self.connected
    
    def disconnect(self) -> bool:
        """Disconnect from the device."""
        if self.connected:
            self.connected = False
            logger.info("Disconnected from Mock ModbusRTU device")
        return True
    
    def read_coils(self, unit_id: int, address: int, count: int) -> List[bool]:
        """Read coil values from the device."""
        try:
            logger.info(f"Reading {count} coils from unit {unit_id}, address {address}")
            return [self.mock_state['coils'].get(address + i, False) for i in range(count)]
        except Exception as e:
            logger.error(f"Error reading coils: {e}")
            return []
    
    def read_discrete_inputs(self, unit_id: int, address: int, count: int) -> List[bool]:
        """Read discrete input values from the device."""
        try:
            logger.info(f"Reading {count} discrete inputs from unit {unit_id}, address {address}")
            return [self.mock_state['discrete_inputs'].get(address + i, False) for i in range(count)]
        except Exception as e:
            logger.error(f"Error reading discrete inputs: {e}")
            return []
    
    def read_holding_registers(self, unit_id: int, address: int, count: int) -> List[int]:
        """Read holding register values from the device."""
        try:
            logger.info(f"Reading {count} holding registers from unit {unit_id}, address {address}")
            return [self.mock_state['holding_registers'].get(address + i, 0) for i in range(count)]
        except Exception as e:
            logger.error(f"Error reading holding registers: {e}")
            return []
    
    def read_input_registers(self, unit_id: int, address: int, count: int) -> List[int]:
        """Read input register values from the device."""
        try:
            logger.info(f"Reading {count} input registers from unit {unit_id}, address {address}")
            return [self.mock_state['input_registers'].get(address + i, 0) for i in range(count)]
        except Exception as e:
            logger.error(f"Error reading input registers: {e}")
            return []
    
    def write_single_coil(self, unit_id: int, address: int, value: bool) -> bool:
        """Write a single coil value to the device."""
        try:
            logger.info(f"Writing coil at address {address} to {value} for unit {unit_id}")
            self.mock_state['coils'][address] = value
            return True
        except Exception as e:
            logger.error(f"Error writing single coil: {e}")
            return False
    
    def write_single_register(self, unit_id: int, address: int, value: int) -> bool:
        """Write a single register value to the device."""
        try:
            logger.info(f"Writing register at address {address} to {value} for unit {unit_id}")
            self.mock_state['holding_registers'][address] = value
            return True
        except Exception as e:
            logger.error(f"Error writing single register: {e}")
            return False
    
    def write_multiple_coils(self, unit_id: int, address: int, values: List[bool]) -> bool:
        """Write multiple coil values to the device."""
        try:
            logger.info(f"Writing {len(values)} coils starting at address {address} for unit {unit_id}")
            for i, value in enumerate(values):
                self.mock_state['coils'][address + i] = value
            return True
        except Exception as e:
            logger.error(f"Error writing multiple coils: {e}")
            return False
    
    def write_multiple_registers(self, unit_id: int, address: int, values: List[int]) -> bool:
        """Write multiple register values to the device."""
        try:
            logger.info(f"Writing {len(values)} registers starting at address {address} for unit {unit_id}")
            for i, value in enumerate(values):
                self.mock_state['holding_registers'][address + i] = value
            return True
        except Exception as e:
            logger.error(f"Error writing multiple registers: {e}")
            return False
    
    def get_device_state(self, unit_id: int) -> Dict[str, Any]:
        """Get the current state of the device."""
        try:
            logger.info(f"Getting device state for unit {unit_id}")
            return {
                'unit_id': unit_id,
                'coils_count': len(self.mock_state['coils']),
                'discrete_inputs_count': len(self.mock_state['discrete_inputs']),
                'holding_registers_count': len(self.mock_state['holding_registers']),
                'input_registers_count': len(self.mock_state['input_registers']),
                'last_read': self.mock_state.get('last_read', {}),
                'last_write': self.mock_state.get('last_write', {})
            }
        except Exception as e:
            logger.error(f"Error getting device state: {e}")
            return {}
    
    def dump_device_state(self, unit_id: int, directory: str = None) -> bool:
        """Simulate dumping the device state to a file."""
        try:
            logger.info(f"Simulating device state dump for unit {unit_id}")
            return True
        except Exception as e:
            logger.error(f"Error dumping device state: {e}")
            return False
    
    def auto_detect(self, baudrates: List[int] = None, unit_ids: List[int] = None) -> Dict[str, Any]:
        """Simulate auto-detection of Modbus RTU devices."""
        try:
            logger.info("Simulating auto-detection of Modbus RTU devices")
            # Always return a successful detection in mock mode
            return {
                'detected': True,
                'unit_id': 1,
                'baudrate': 9600,
                'function_code': 3  # Read holding registers
            }
        except Exception as e:
            logger.error(f"Error in auto-detection: {e}")
            return {'detected': False, 'error': str(e)}
