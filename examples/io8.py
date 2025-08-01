#!/usr/bin/env python3
"""
Single device service example
"""
from devices.registry.waveshare.io_8ch import WaveshareIO8CH
from devices.base.service import DeviceService


class IO8CHService(DeviceService):
    """Service for single Waveshare IO 8CH device"""

    def setup_routes(self):
        """Add custom routes for IO operations"""

        @self.app.route('/outputs/toggle/<int:channel>', methods=['POST'])
        def toggle_output(channel):
            device = list(self.devices.values())[0] if self.devices else None
            if device and 0 <= channel < 8:
                current = device.read_register(f'output_{channel}')
                success = device.write_register(f'output_{channel}', not current)
                return {'success': success, 'new_state': not current}
            return {'error': 'Invalid channel or no device'}, 400


# Create and start service
if __name__ == '__main__':
    # Create service
    service = IO8CHService('IO8CH_Service', port=5001)

    # Create device
    device = WaveshareIO8CH(
        device_id='io8ch_1',
        port='/dev/ttyUSB0',
        unit_id=1,
        baudrate=9600
    )

    # Add device to service
    service.add_device(device)

    # Start service
    service.start(host='0.0.0.0', debug=True)

    print(f"Service running on http://localhost:5001")
    print("Endpoints:")
    print("  GET  /health")
    print("  GET  /devices")
    print("  GET  /devices/io8ch_1")
    print("  POST /outputs/toggle/0")

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()