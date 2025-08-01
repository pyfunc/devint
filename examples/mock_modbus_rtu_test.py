#!/usr/bin/env python3
"""
Example script to test the Mock ModbusRTU protocol implementation in devint.
This script allows testing without requiring physical hardware.
"""

import logging
import os
import sys
import time

# Add devint to path if not installed
devint_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if os.path.exists(devint_path) and devint_path not in sys.path:
    sys.path.append(devint_path)

from devint.protocols.mock_modbus_rtu import MockModbusRTUProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test the Mock ModbusRTU protocol implementation."""
    # Default port (ignored in mock mode, but kept for API consistency)
    port = '/dev/ttyUSB0'
    
    # Check if a port was specified as a command-line argument
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    logger.info(f"Initializing Mock ModbusRTU protocol (simulated port: {port})")
    
    # Initialize the Mock ModbusRTU protocol
    try:
        modbus = MockModbusRTUProtocol(
            port=port,
            baudrate=9600,  # Common default baudrate (ignored in mock)
            timeout=1.0,
            rs485_delay=0.005,
            enable_state_tracking=True
        )
        
        if not modbus.is_connected():
            logger.error(f"Failed to connect to Mock ModbusRTU device")
            return
        
        logger.info("Connected to Mock ModbusRTU device")
        
        # Try to auto-detect devices
        logger.info("Attempting to auto-detect Modbus devices (simulated)...")
        detection_result = modbus.auto_detect()
        logger.info(f"Auto-detection result: {detection_result}")
        
        # If a device was detected, use its unit_id
        unit_id = detection_result.get('unit_id', 1) if detection_result.get('detected') else 1
        
        # Read some registers
        logger.info(f"Reading holding registers from unit {unit_id}, address 0, count 10")
        registers = modbus.read_holding_registers(unit_id, 0, 10)
        logger.info(f"Holding registers: {registers}")
        
        # Read some coils
        logger.info(f"Reading coils from unit {unit_id}, address 0, count 10")
        coils = modbus.read_coils(unit_id, 0, 10)
        logger.info(f"Coils: {coils}")
        
        # Write a register
        logger.info(f"Writing value 12345 to holding register at address 5, unit {unit_id}")
        write_result = modbus.write_single_register(unit_id, 5, 12345)
        logger.info(f"Write result: {write_result}")
        
        # Read back the register we just wrote
        logger.info(f"Reading back holding register at address 5, unit {unit_id}")
        register_value = modbus.read_holding_registers(unit_id, 5, 1)
        logger.info(f"Register value: {register_value}")
        
        # Write multiple registers
        logger.info(f"Writing values [100, 200, 300] to holding registers starting at address 10, unit {unit_id}")
        write_result = modbus.write_multiple_registers(unit_id, 10, [100, 200, 300])
        logger.info(f"Write result: {write_result}")
        
        # Read back the registers we just wrote
        logger.info(f"Reading back holding registers at addresses 10-12, unit {unit_id}")
        register_values = modbus.read_holding_registers(unit_id, 10, 3)
        logger.info(f"Register values: {register_values}")
        
        # Get device state
        logger.info(f"Getting device state for unit {unit_id}")
        state = modbus.get_device_state(unit_id)
        logger.info(f"Device state: {state}")
        
        # Dump device state to file
        logger.info(f"Dumping device state for unit {unit_id}")
        modbus.dump_device_state(unit_id)
        
        # Disconnect
        logger.info("Disconnecting from Mock ModbusRTU device")
        modbus.disconnect()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return

if __name__ == "__main__":
    main()
