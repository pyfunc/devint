#!/usr/bin/env python3
"""
Comprehensive edge case testing for ModbusRTUDevice class.

This script tests various edge cases and error handling scenarios for the ModbusRTUDevice class:
1. Invalid register names
2. Out-of-range addresses
3. Invalid value types
4. Connection failures
5. Error handling during read/write operations
6. Boundary conditions
"""

import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.append('/home/tom/github/pyfunc/devint')

from devint.services.multi_service import MultiDeviceService
from devint.registry.modbus.rtu_device import ModbusRTUDevice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_invalid_register_names(device: ModbusRTUDevice) -> Dict[str, Any]:
    """Test handling of invalid register names."""
    results = {}
    
    # Test case: Empty register name
    logger.info("Testing empty register name")
    result = device.read_register("")
    results["empty"] = result is None
    logger.info(f"Empty register name result: {result}")
    
    # Test case: Invalid format (no underscore)
    logger.info("Testing invalid format (no underscore)")
    result = device.read_register("coil5")
    results["no_underscore"] = result is None
    logger.info(f"Invalid format result: {result}")
    
    # Test case: Invalid register type
    logger.info("Testing invalid register type")
    result = device.read_register("unknown_5")
    results["invalid_type"] = result is None
    logger.info(f"Invalid register type result: {result}")
    
    # Test case: Non-numeric address
    logger.info("Testing non-numeric address")
    result = device.read_register("coil_abc")
    results["non_numeric"] = result is None
    logger.info(f"Non-numeric address result: {result}")
    
    # Test case: Multiple underscores
    logger.info("Testing multiple underscores")
    result = device.read_register("coil_5_extra")
    results["multiple_underscores"] = result is None
    logger.info(f"Multiple underscores result: {result}")
    
    return results


def test_address_boundaries(device: ModbusRTUDevice) -> Dict[str, Any]:
    """Test address boundary conditions."""
    results = {}
    
    # Test case: Address 0 (lower boundary)
    logger.info("Testing address 0 (lower boundary)")
    result = device.read_register("coil_0")
    results["address_0"] = result is not None
    logger.info(f"Address 0 result: {result}")
    
    # Test case: Very large address (near upper boundary)
    logger.info("Testing very large address (65535)")
    result = device.read_register("holding_65535")
    results["address_max"] = result is not None
    logger.info(f"Large address result: {result}")
    
    # Test case: Negative address
    logger.info("Testing negative address")
    result = device.read_register("coil_-1")
    results["negative_address"] = result is None
    logger.info(f"Negative address result: {result}")
    
    return results


def test_value_type_handling(device: ModbusRTUDevice) -> Dict[str, Any]:
    """Test handling of different value types for writing."""
    results = {}
    
    # Test case: Boolean values for coils
    logger.info("Testing boolean values for coils")
    result_true = device.write_register("coil_10", True)
    result_false = device.write_register("coil_11", False)
    results["boolean_values"] = result_true and result_false
    logger.info(f"Boolean values results: True={result_true}, False={result_false}")
    
    # Test case: Integer values for holding registers
    logger.info("Testing integer values for holding registers")
    result_int = device.write_register("holding_10", 12345)
    results["integer_value"] = result_int
    logger.info(f"Integer value result: {result_int}")
    
    # Test case: String value (should be converted or rejected)
    logger.info("Testing string value for holding register")
    result_str = device.write_register("holding_11", "12345")
    results["string_value"] = result_str  # Should convert to int if possible
    logger.info(f"String value result: {result_str}")
    
    # Test case: Float value (should be converted or rejected)
    logger.info("Testing float value for holding register")
    result_float = device.write_register("holding_12", 123.45)
    results["float_value"] = result_float  # Should truncate to int
    logger.info(f"Float value result: {result_float}")
    
    # Test case: Out of range value for holding register
    logger.info("Testing out of range value for holding register (65536)")
    result_large = device.write_register("holding_13", 65536)
    results["large_value"] = result_large  # Implementation-dependent
    logger.info(f"Large value result: {result_large}")
    
    # Test case: Negative value for holding register
    logger.info("Testing negative value for holding register")
    result_negative = device.write_register("holding_14", -1)
    results["negative_value"] = result_negative  # Implementation-dependent
    logger.info(f"Negative value result: {result_negative}")
    
    return results


def test_connection_handling(device_config: Dict[str, Any]) -> Dict[str, Any]:
    """Test handling of connection issues."""
    results = {}
    
    # Test case: Invalid port
    logger.info("Testing invalid port")
    invalid_device = ModbusRTUDevice(
        device_id="invalid_device",
        port="/dev/nonexistent",
        baudrate=9600,
        unit_id=1,
        mock_mode=False  # Real mode to test connection failure
    )
    
    # Should not be connected
    results["invalid_port_connected"] = not invalid_device.connected
    logger.info(f"Invalid port connected: {invalid_device.connected}")
    
    # Read should fail gracefully
    read_result = invalid_device.read_register("coil_0")
    results["invalid_port_read"] = read_result is None
    logger.info(f"Invalid port read result: {read_result}")
    
    # Write should fail gracefully
    write_result = invalid_device.write_register("coil_0", True)
    results["invalid_port_write"] = not write_result
    logger.info(f"Invalid port write result: {write_result}")
    
    return results


def test_read_write_consistency(device: ModbusRTUDevice) -> Dict[str, Any]:
    """Test consistency between read and write operations."""
    results = {}
    
    # Test case: Write and read back coil
    logger.info("Testing write and read back coil")
    write_result = device.write_register("coil_20", True)
    read_result = device.read_register("coil_20")
    results["coil_consistency"] = write_result and read_result is True
    logger.info(f"Coil consistency: write={write_result}, read={read_result}")
    
    # Test case: Write and read back holding register
    logger.info("Testing write and read back holding register")
    test_value = 54321
    write_result = device.write_register("holding_20", test_value)
    read_result = device.read_register("holding_20")
    results["holding_consistency"] = write_result and read_result == test_value
    logger.info(f"Holding consistency: write={write_result}, read={read_result}")
    
    return results


def run_edge_case_tests() -> None:
    """Run all edge case tests."""
    logger.info("Starting comprehensive edge case tests for ModbusRTUDevice")
    
    # Create a MultiDeviceService
    logger.info("Creating MultiDeviceService")
    service = MultiDeviceService()
    
    # Create a ModbusRTUDevice in mock mode
    logger.info("Creating ModbusRTUDevice in mock mode")
    
    modbus_device = ModbusRTUDevice(  # type: ignore
        device_id="modbus_rtu_edge_test",
        port="/dev/ttyACM0",
        baudrate=9600,
        unit_id=1,
        mock_mode=True  # Use mock mode for testing
    )
    
    # Add device to service
    logger.info("Adding device to service")
    service.add_device(modbus_device)
    
    # Run all test categories
    test_results = {}
    
    try:
        # Test invalid register names
        test_results["invalid_register_names"] = test_invalid_register_names(modbus_device)
        
        # Test address boundaries
        test_results["address_boundaries"] = test_address_boundaries(modbus_device)
        
        # Test value type handling
        test_results["value_type_handling"] = test_value_type_handling(modbus_device)
        
        # Test connection handling
        test_results["connection_handling"] = test_connection_handling({
            "device_id": modbus_device.device_id,
            "port": modbus_device.port,
            "baudrate": modbus_device.baudrate,
            "unit_id": modbus_device.unit_id
        })
        
        # Test read/write consistency
        test_results["read_write_consistency"] = test_read_write_consistency(modbus_device)
        
        # Summarize results
        logger.info("Test results summary:")
        for category, results in test_results.items():
            logger.info(f"  {category}:")
            for test, result in results.items():
                logger.info(f"    {test}: {'PASS' if result else 'FAIL'}")
        
    except Exception as e:
        logger.error(f"Error during tests: {e}")
    finally:
        # Clean up
        logger.info("Shutting down device")
        modbus_device.shutdown()
        
        logger.info("Removing device from service")
        service.remove_device(modbus_device.device_id)
    
    logger.info("Edge case tests completed")


if __name__ == "__main__":
    run_edge_case_tests()
