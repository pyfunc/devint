# ModbusRTUDevice Documentation

## Overview

The `ModbusRTUDevice` class provides an implementation of the DevInt `BaseDevice` interface for Modbus RTU protocol devices. It serves as a bridge between the DevInt device management framework and the Modbus RTU protocol implementation from the ModAPI project.

This class enables communication with Modbus RTU devices over serial connections, supporting both real hardware devices and mock devices for testing without physical hardware.

## Class Hierarchy

```
BaseDevice (Abstract)
    └── ModbusRTUDevice
```

## Features

- Full implementation of the `BaseDevice` interface
- Support for all Modbus RTU register types:
  - Coils (read/write)
  - Discrete Inputs (read-only)
  - Holding Registers (read/write)
  - Input Registers (read-only)
- Register-based access using a simple naming convention
- Automatic type conversion for register values
- Comprehensive error handling and logging
- Mock mode for hardware-independent testing
- Device state tracking and dumping
- Auto-detection of Modbus RTU devices

## Constructor

```python
ModbusRTUDevice(
    device_id: str,
    port: str,
    baudrate: int = 9600,
    unit_id: int = 1,
    timeout: float = 1.0,
    mock_mode: bool = False,
    **kwargs
)
```

### Parameters

- `device_id` (str): Unique identifier for the device
- `port` (str): Serial port path (e.g., '/dev/ttyUSB0', 'COM1')
- `baudrate` (int, optional): Serial baudrate. Default: 9600
- `unit_id` (int, optional): Modbus unit/slave ID. Default: 1
- `timeout` (float, optional): Communication timeout in seconds. Default: 1.0
- `mock_mode` (bool, optional): If True, use mock implementation. Default: False
- `**kwargs`: Additional parameters passed to the underlying protocol implementation

## Register Access API

The `ModbusRTUDevice` class implements the `BaseDevice` interface's register access methods:

### read_register

```python
def read_register(self, register_name: str) -> Any:
    """Read a register by name."""
```

Reads a value from a register identified by name.

#### Register Naming Convention

Register names follow the format: `type_address` where:
- `type` is one of:
  - `coil`: Coils (read/write)
  - `discrete`: Discrete inputs (read-only)
  - `holding`: Holding registers (read/write)
  - `input`: Input registers (read-only)
- `address` is the numeric address of the register (0-65535)

Examples:
- `coil_0`: Coil at address 0
- `discrete_100`: Discrete input at address 100
- `holding_400`: Holding register at address 400
- `input_300`: Input register at address 300

#### Return Value

- For coils and discrete inputs: Boolean value (`True` or `False`)
- For holding and input registers: Integer value
- `None` if the read operation fails

### write_register

```python
def write_register(self, register_name: str, value: Any) -> bool:
    """Write to a register by name."""
```

Writes a value to a register identified by name.

#### Register Naming Convention

Same as for `read_register`.

#### Parameters

- `register_name` (str): Register name in the format `type_address`
- `value` (Any): Value to write
  - For coils: Will be converted to boolean
  - For holding registers: Will be converted to integer
  - Writing to discrete inputs or input registers will fail (read-only)

#### Return Value

- `True` if the write operation succeeds
- `False` if the write operation fails

## Direct Modbus RTU Access

In addition to the register-based API, the `ModbusRTUDevice` class provides direct access to the underlying Modbus RTU protocol methods:

### read_coils

```python
def read_coils(self, address: int, count: int) -> List[bool]:
    """Read coils (function code 0x01)."""
```

### read_discrete_inputs

```python
def read_discrete_inputs(self, address: int, count: int) -> List[bool]:
    """Read discrete inputs (function code 0x02)."""
```

### read_holding_registers

```python
def read_holding_registers(self, address: int, count: int) -> List[int]:
    """Read holding registers (function code 0x03)."""
```

### read_input_registers

```python
def read_input_registers(self, address: int, count: int) -> List[int]:
    """Read input registers (function code 0x04)."""
```

### write_single_coil

```python
def write_single_coil(self, address: int, value: bool) -> bool:
    """Write single coil (function code 0x05)."""
```

### write_single_register

```python
def write_single_register(self, address: int, value: int) -> bool:
    """Write single register (function code 0x06)."""
```

### write_multiple_coils

```python
def write_multiple_coils(self, address: int, values: List[bool]) -> bool:
    """Write multiple coils (function code 0x0F)."""
```

### write_multiple_registers

```python
def write_multiple_registers(self, address: int, values: List[int]) -> bool:
    """Write multiple registers (function code 0x10)."""
```

## Device Management

### connect

```python
def connect(self) -> bool:
    """Connect to the device."""
```

Establishes a connection to the Modbus RTU device.

### disconnect

```python
def disconnect(self) -> bool:
    """Disconnect from the device."""
```

Closes the connection to the Modbus RTU device.

### shutdown

```python
def shutdown(self) -> bool:
    """Shut down the device."""
```

Performs a clean shutdown of the device, including disconnection.

### get_status

```python
def get_status(self) -> Dict[str, Any]:
    """Get the device status."""
```

Returns a dictionary with the current device status, including:
- `device_id`: Device identifier
- `device_type`: "ModbusRTU"
- `connected`: Connection status
- `unit_id`: Modbus unit/slave ID
- `port`: Serial port path
- `baudrate`: Serial baudrate
- `mock_mode`: Whether mock mode is enabled
- `device_state`: Current device state information

### dump_device_state

```python
def dump_device_state(self, directory: str = None) -> bool:
    """Dump the device state to a file."""
```

Dumps the current device state to a file in the specified directory.

### auto_detect

```python
def auto_detect(self, baudrates: List[int] = None, unit_ids: List[int] = None) -> Dict[str, Any]:
    """Auto-detect Modbus RTU devices."""
```

Attempts to auto-detect Modbus RTU devices by scanning different baudrates and unit IDs.

## Mock Mode

The `ModbusRTUDevice` class supports a mock mode for testing without physical hardware. When `mock_mode=True` is specified in the constructor, the device will use a simulated Modbus RTU implementation that behaves like a real device but doesn't require actual hardware.

This is useful for:
- Development without physical hardware
- Automated testing
- Demonstration purposes
- Debugging application logic

## Error Handling

The `ModbusRTUDevice` class includes comprehensive error handling:

- Connection failures are logged and reported
- Invalid register names are detected and reported
- Type conversion errors are caught and logged
- Read/write errors from the underlying protocol are handled gracefully
- All errors are logged with appropriate context information

## Example Usage

### Basic Usage

```python
from devint.registry.modbus.rtu_device import ModbusRTUDevice

# Create a ModbusRTU device
device = ModbusRTUDevice(
    device_id="modbus_device_1",
    port="/dev/ttyUSB0",
    baudrate=9600,
    unit_id=1
)

# Connect to the device
device.connect()

# Read a register using the register-based API
coil_value = device.read_register("coil_0")
holding_value = device.read_register("holding_100")

# Write to a register using the register-based API
device.write_register("coil_1", True)
device.write_register("holding_200", 12345)

# Use direct Modbus RTU methods
coils = device.read_coils(0, 10)
device.write_multiple_registers(300, [100, 200, 300])

# Disconnect when done
device.disconnect()
```

### Using with MultiDeviceService

```python
from devint.services.multi_service import MultiDeviceService
from devint.registry.modbus.rtu_device import ModbusRTUDevice

# Create a MultiDeviceService
service = MultiDeviceService()

# Create a ModbusRTU device
modbus_device = ModbusRTUDevice(
    device_id="modbus_rtu_1",
    port="/dev/ttyUSB0",
    baudrate=9600,
    unit_id=1
)

# Add device to service
service.add_device(modbus_device)

# Use the device through the service
service.read_register("modbus_rtu_1", "holding_100")
service.write_register("modbus_rtu_1", "coil_5", True)

# Remove device when done
service.remove_device("modbus_rtu_1")
```

### Using Mock Mode

```python
from devint.registry.modbus.rtu_device import ModbusRTUDevice

# Create a ModbusRTU device in mock mode
device = ModbusRTUDevice(
    device_id="mock_modbus",
    port="/dev/ttyUSB0",  # Port doesn't need to exist in mock mode
    baudrate=9600,
    unit_id=1,
    mock_mode=True  # Enable mock mode
)

# Use the device as if it were a real device
device.connect()
coil_value = device.read_register("coil_0")
device.write_register("holding_100", 12345)
device.disconnect()
```

## Best Practices

1. **Always check connection status** before performing operations
2. **Use appropriate error handling** when reading/writing registers
3. **Disconnect properly** when done with the device
4. **Use mock mode** for development and testing
5. **Use the register-based API** for compatibility with the DevInt framework
6. **Use direct Modbus RTU methods** for advanced operations

## Troubleshooting

### Common Issues

1. **Connection failures**
   - Check that the port exists and is accessible
   - Verify baudrate settings
   - Ensure the device is powered on

2. **No response from device**
   - Verify unit ID is correct
   - Check wiring and connections
   - Increase timeout value

3. **Invalid register values**
   - Verify register addresses
   - Check data types and conversions
   - Ensure register exists on the device

4. **Permission issues**
   - Ensure user has permission to access serial ports
   - Check port is not in use by another application

### Debugging

The `ModbusRTUDevice` class uses Python's logging system for detailed logging. To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will provide detailed information about:
- Connection attempts
- Register read/write operations
- Error conditions
- Device state changes
