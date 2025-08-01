#!/usr/bin/env python3
"""
Example script to test the ModbusRTU protocol implementation in devint.
"""

import logging
import os
import sys
import time

# Add devint to path if not installed
devint_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if os.path.exists(devint_path) and devint_path not in sys.path:
    sys.path.append(devint_path)

from devint.protocols.modbus_rtu import ModbusRTUProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test the ModbusRTU protocol implementation."""
    # Default port for most USB-to-RS485 adapters
    port = '/dev/ttyUSB0'
    
    # Check if a port was specified as a command-line argument
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    logger.info(f"Initializing ModbusRTU protocol on port {port}")
    
    # Initialize the ModbusRTU protocol
    try:
        modbus = ModbusRTUProtocol(
            port=port,
            baudrate=19200,  # Common default baudrate
            timeout=1.0,
            rs485_delay=0.005,
            enable_state_tracking=True
        )
        
        if not modbus.is_connected():
            logger.error(f"Failed to connect to ModbusRTU device on {port}")
            return
        
        logger.info("Connected to ModbusRTU device")
        
        # Try to auto-detect devices
        logger.info("Attempting to auto-detect Modbus devices...")
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
        
        # Get device state
        logger.info(f"Getting device state for unit {unit_id}")
        state = modbus.get_device_state(unit_id)
        logger.info(f"Device state: {state}")
        
        # Dump device state to file
        logger.info(f"Dumping device state for unit {unit_id}")
        modbus.dump_device_state(unit_id)
        
        # Disconnect
        logger.info("Disconnecting from ModbusRTU device")
        modbus.disconnect()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return

if __name__ == "__main__":
    main()
