#!/usr/bin/env python3
"""
Auto-discovery and configuration example
"""
from devices.device_manager import DeviceManager
from devices.services.discovery import DiscoveryService

# Create device manager
manager = DeviceManager()

# Register device types
from devices.registry.waveshare import WaveshareIO8CH
from devices.registry.raspberry_pi import RaspberrySenseHAT

manager.register_device_type('WaveshareIO8CH', WaveshareIO8CH)
manager.register_device_type('RaspberrySenseHAT', RaspberrySenseHAT)

# Discover devices
print("Scanning for devices...")

# Scan I2C buses
i2c_devices = manager.discover_devices('i2c')
print(f"Found {len(i2c_devices)} I2C devices")

# Scan serial ports
serial_devices = manager.discover_devices('serial')
print(f"Found {len(serial_devices)} serial devices")

# Add discovered devices
for device in i2c_devices + serial_devices:
    manager.add_device(device)

# Save configuration
manager.save_configuration()
print("Configuration saved to devices.json")

# Start web interface for all devices
from devices.services.multi_service import MultiDeviceService

service = MultiDeviceService('Discovery_Service', port=5000)
for device in manager.devices.values():
    service.add_device(device)

service.start()
print(f"Service running with {len(manager.devices)} devices")