#!/usr/bin/env python3
"""
Example script to test the ModbusRTUDevice class with the DevInt framework.
This script uses mock mode to test without requiring physical hardware.
"""

import logging
import os
import sys
import time

# Add devint to path if not installed
devint_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if os.path.exists(devint_path) and devint_path not in sys.path:
    sys.path.append(devint_path)

from devint.registry.modbus.rtu_device import ModbusRTUDevice
from devint.services.multi_service import MultiDeviceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test the ModbusRTUDevice class with the DevInt framework."""
    # Create a device service
    logger.info("Creating MultiDeviceService")
    service = MultiDeviceService()
    
    # Create a ModbusRTU device in mock mode
    logger.info("Creating ModbusRTUDevice in mock mode")
    modbus_device = ModbusRTUDevice(
        device_id="modbus_rtu_1",
        unit_id=1,
        port="/dev/ttyUSB0",  # Ignored in mock mode
        baudrate=9600,        # Ignored in mock mode
        mock_mode=True        # Use mock mode (no physical hardware required)
    )
    
    # Add the device to the service
    logger.info("Adding device to service")
    service.add_device(modbus_device)
    
    # Get device status
    logger.info("Getting device status")
    status = modbus_device.get_status()
    logger.info(f"Device status: {status}")
    
    # Read some registers
    logger.info("Reading holding registers")
    registers = modbus_device.read_holding_registers(0, 10)
    logger.info(f"Holding registers: {registers}")
    
    # Read some coils
    logger.info("Reading coils")
    coils = modbus_device.read_coils(0, 10)
    logger.info(f"Coils: {coils}")
    
    # Write a register
    logger.info("Writing value 12345 to holding register at address 5")
    write_result = modbus_device.write_single_register(5, 12345)
    logger.info(f"Write result: {write_result}")
    
    # Read back the register we just wrote
    logger.info("Reading back holding register at address 5")
    register_value = modbus_device.read_holding_registers(5, 1)
    logger.info(f"Register value: {register_value}")
    
    # Write multiple registers
    logger.info("Writing values [100, 200, 300] to holding registers starting at address 10")
    write_result = modbus_device.write_multiple_registers(10, [100, 200, 300])
    logger.info(f"Write result: {write_result}")
    
    # Read back the registers we just wrote
    logger.info("Reading back holding registers at addresses 10-12")
    register_values = modbus_device.read_holding_registers(10, 3)
    logger.info(f"Register values: {register_values}")
    
    # Dump device state
    logger.info("Dumping device state")
    modbus_device.dump_device_state()
    
    # Shutdown the device
    logger.info("Shutting down device")
    modbus_device.shutdown()
    
    # Remove the device from the service
    logger.info("Removing device from service")
    service.remove_device("modbus_rtu_1")
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    main()
