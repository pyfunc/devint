#!/usr/bin/env python3
"""
Example of dynamic parameter changes
"""
from devint.registry.waveshare.io_8ch import WaveshareIO8CH

# Create device
device = WaveshareIO8CH(
    device_id='dynamic_device',
    port='/dev/ttyACM0',
    unit_id=1,
    baudrate=9600
)

# Initialize
if device.initialize():
    print(f"Device initialized with baudrate: {device.interfaces['primary'].get_parameter('baudrate')}")

    # Read some data
    output_state = device.read_register('output_0')
    print(f"Output 0 state: {output_state}")

    # Change baudrate dynamically
    print("\nChanging baudrate to 19200...")
    success = device.interfaces['primary'].set_parameter('baudrate', 19200)

    if success:
        print(f"New baudrate: {device.interfaces['primary'].get_parameter('baudrate')}")

        # Continue operations with new baudrate
        output_state = device.read_register('output_0')
        print(f"Output 0 state after baudrate change: {output_state}")
    else:
        print("Failed to change baudrate")
else:
    print("Failed to initialize device")