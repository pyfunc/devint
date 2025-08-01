#!/usr/bin/env python3
"""
Multi-device service for Raspberry Pi with various HATs and modules
"""
from devint.services.multi_service import MultiDeviceService
from devint.registry.waveshare.io_8ch import WaveshareIO8CH
from devint.registry.raspberry_pi.sense_hat import RaspberrySenseHAT
from devint.registry.waveshare.analog_8ch import WaveshareAnalog8CH


def main():
    # Create multi-device service
    service = MultiDeviceService('RPi_MultiDevice', port=5000)

    # Add Sense HAT (I2C)
    sense_hat = RaspberrySenseHAT(
        device_id='sense_hat_1',
        i2c_bus=1
    )
    service.add_device(sense_hat)

    # Add Waveshare IO 8CH (Serial/Modbus)
    io_module = WaveshareIO8CH(
        device_id='io_module_1',
        port='/dev/ttyACM0',
        unit_id=1,
        baudrate=9600
    )
    service.add_device(io_module)

    # Add another IO module with different baudrate
    io_module2 = WaveshareIO8CH(
        device_id='io_module_2',
        port='/dev/ttyUSB1',
        unit_id=2,
        baudrate=19200  # Different baudrate
    )
    service.add_device(io_module2)

    # Start service
    service.start(host='0.0.0.0', debug=False)

    print("Multi-device service running on http://localhost:5000")
    print("\nDevices:")
    for device_id, device in service.devices.items():
        print(f"  - {device_id}: {device.name}")

    print("\nExample API calls:")
    print("  curl http://localhost:5000/devices")
    print("  curl http://localhost:5000/devices/sense_hat_1/registers/temperature")
    print("  curl -X PUT http://localhost:5000/devices/io_module_1/parameters \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"interface\": \"primary\", \"parameters\": {\"baudrate\": 38400}}'")

    # Keep running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()


if __name__ == '__main__':
    main()