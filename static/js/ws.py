from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import threading
import time
from typing import Dict, Any


class WebSocketAPI:
    def __init__(self, app: Flask, device_manager):
        self.app = app
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self.device_manager = device_manager
        self.clients = {}

        self.setup_handlers()
        self.start_background_tasks()

    def setup_handlers(self):
        @self.socketio.on('connect')
        def handle_connect():
            client_id = request.sid
            self.clients[client_id] = {
                'connected_at': time.time(),
                'subscriptions': set()
            }
            print(f"Client {client_id} connected")

            # Send initial devices list
            devices_data = [device.to_dict() for device in self.device_manager.devices.values()]
            emit('devices_list', devices_data)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            client_id = request.sid
            if client_id in self.clients:
                del self.clients[client_id]
            print(f"Client {client_id} disconnected")

        @self.socketio.on('get_devices')
        def handle_get_devices(data):
            devices_data = [device.to_dict() for device in self.device_manager.devices.values()]
            emit('devices_list', devices_data)

        @self.socketio.on('read_register')
        def handle_read_register(data):
            device_id = data.get('device_id')
            register = data.get('register')

            device = self.device_manager.get_device(device_id)
            if device:
                value = device.read_register(register)
                emit('register_update', {
                    'device_id': device_id,
                    'register': register,
                    'value': value
                })

        @self.socketio.on('write_register')
        def handle_write_register(data):
            device_id = data.get('device_id')
            register = data.get('register')
            value = data.get('value')

            device = self.device_manager.get_device(device_id)
            if device:
                success = device.write_register(register, value)
                if success:
                    # Broadcast update to all clients
                    self.socketio.emit('register_update', {
                        'device_id': device_id,
                        'register': register,
                        'value': value
                    })
                else:
                    emit('error', {'message': f'Failed to write register {register}'})

        @self.socketio.on('scan_devices')
        def handle_scan_devices(data):
            ports = data.get('ports', [])
            baudrates = data.get('baudrates', [9600, 19200, 38400, 115200])

            # Run scan in background
            threading.Thread(
                target=self._scan_devices_async,
                args=(request.sid, ports, baudrates)
            ).start()

        @self.socketio.on('add_device')
        def handle_add_device(data):
            # Add device based on scan result
            port = data.get('port')
            baudrate = data.get('baudrate')
            unit_id = data.get('unit_id', 1)
            device_type = data.get('type', 'WaveshareIO8CH')

            # Create device instance
            if device_type == 'auto_detect' or device_type == 'WaveshareIO8CH':
                from devices.registry.waveshare import WaveshareIO8CH
                device = WaveshareIO8CH(
                    device_id=f"waveshare_{port.replace('/', '_')}_{unit_id}",
                    port=port,
                    unit_id=unit_id,
                    baudrate=baudrate
                )

                if device.initialize():
                    self.device_manager.add_device(device)
                    emit('device_added', device.to_dict())

                    # Broadcast to all clients
                    self.socketio.emit('devices_list',
                                       [d.to_dict() for d in self.device_manager.devices.values()])
                else:
                    emit('error', {'message': 'Failed to initialize device'})

    def _scan_devices_async(self, client_id, ports, baudrates):
        """Async device scanning"""
        results = []

        for port in ports:
            for baudrate in baudrates:
                for unit_id in [1, 2, 3, 247]:  # Common unit IDs
                    # Use existing scan logic
                    success = test_modbus_port(port, baudrate, unit_id)
                    if success:
                        result = {
                            'port': port,
                            'baudrate': baudrate,
                            'unit_id': unit_id
                        }
                        results.append(result)

                        # Send intermediate result
                        self.socketio.emit('scan_result', [result], room=client_id)

        # Send completion
        self.socketio.emit('scan_complete', {'found': len(results)}, room=client_id)

    def start_background_tasks(self):
        """Start background tasks for periodic updates"""

        def update_loop():
            while True:
                time.sleep(1)  # Update every second

                # Update all devices
                for device in self.device_manager.devices.values():
                    if device.is_online:
                        # Read inputs and outputs
                        try:
                            # This would be device-specific
                            if hasattr(device, 'get_all_inputs'):
                                inputs = device.get_all_inputs()
                                outputs = device.get_all_outputs()

                                # Broadcast updates
                                self.socketio.emit('device_update', device.to_dict())
                        except Exception as e:
                            print(f"Error updating device {device.device_id}: {e}")

        # Start update thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the WebSocket server"""
        self.socketio.run(self.app, host=host, port=port, debug=debug)