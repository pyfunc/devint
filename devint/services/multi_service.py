import threading
from typing import Dict, List, Optional
from devint.base.service import DeviceService
from devint.device_manager import DeviceManager
from flask import jsonify, request


class MultiDeviceService(DeviceService):
    """Service handling multiple devices"""
    
    # Class-level set to track registered routes
    _registered_routes = set()
    _lock = threading.Lock()

    def __init__(self, name: str = "MultiDevice", port: int = 5000):
        super().__init__(name, port)
        self.device_manager = DeviceManager()
        self.app = self.create_app()
        self.setup_routes()
        
    def run(self, host: str = '0.0.0.0', port: int = None, debug: bool = False):
        """Run the web service.
        
        Args:
            host: Host to bind to (default: '0.0.0.0')
            port: Port to listen on (default: self.port)
            debug: Run in debug mode (default: False)
        """
        if port is None:
            port = self.port
            
        self.logger.info(f"Starting {self.name} service on http://{host}:{port}")
        self.logger.info("Press Ctrl+C to stop")
        
        try:
            self.app.run(host=host, port=port, debug=debug)
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
        except Exception as e:
            self.logger.error(f"Error running service: {e}")
            raise

    def _register_route(self, rule, endpoint=None, view_func=None, **options):
        """Helper to register a route only once"""
        with self._lock:
            if rule not in self._registered_routes:
                self.app.add_url_rule(rule, endpoint, view_func, **options)
                self._registered_routes.add(rule)
                return True
            return False

    def setup_routes(self):
        """Setup additional routes for multi-device operations"""
        
        # Root route with API documentation
        @self.app.route('/')
        def root():
            """Root endpoint with API documentation"""
            return {
                'service': 'DevInt Device Manager',
                'version': '0.1.0',
                'endpoints': {
                    '/': 'This documentation',
                    '/health': 'Get service health status',
                    '/devices': 'List all registered devices',
                    '/devices/<device_id>': 'Get device details',
                    '/devices/<device_id>/registers/<register_name>': 'Read/write device register',
                    '/devices/<device_id>/parameters': 'Get/update device parameters',
                    '/scan': 'Scan for devices (POST)',
                    '/devices/batch': 'Batch operations on multiple devices (POST)'
                },
                'documentation': 'https://github.com/pyfunc/devint'
            }
        
        # Define route handlers as instance methods
        def scan_devices():
            """Scan for devices on specified interfaces"""
            data = request.get_json()
            interface_type = data.get('interface', 'serial')

            # Perform scan based on interface type
            if interface_type == 'i2c':
                return self._scan_i2c_devices()
            elif interface_type == 'serial':
                return self._scan_serial_devices(data)
            elif interface_type == 'spi':
                return self._scan_spi_devices()

            return jsonify({'error': 'Unknown interface type'}), 400
            
        # Register the route with a unique endpoint name to avoid conflicts
        self._register_route('/scan', f'scan_devices_{self.name}', scan_devices, methods=['POST'])

        def batch_operation():
            """Perform batch operations on multiple devices"""
            data = request.get_json()
            operations = data.get('operations', [])
            results = []

            for op in operations:
                device_id = op.get('device_id')
                action = op.get('action')
                params = op.get('params', {})

                device = self.devices.get(device_id)
                if device:
                    if action == 'read':
                        value = device.read_register(params.get('register'))
                        results.append({
                            'device_id': device_id,
                            'action': action,
                            'result': value,
                            'success': value is not None
                        })
                    elif action == 'write':
                        success = device.write_register(
                            params.get('register'),
                            params.get('value')
                        )
                        results.append({
                            'device_id': device_id,
                            'action': action,
                            'success': success
                        })

            return jsonify({'results': results})

        def device_parameters(device_id):
            """Get or update device interface parameters"""
            device = self.devices.get(device_id)
            if not device:
                return jsonify({'error': 'Device not found'}), 404

            if request.method == 'GET':
                # Get all interface parameters
                params = {}
                for name, interface in device.interfaces.items():
                    params[name] = interface.config.parameters
                return jsonify(params)
            else:  # PUT
                # Update interface parameters
                data = request.get_json()
                interface_name = data.get('interface', 'primary')
                parameters = data.get('parameters', {})

                interface = device.interfaces.get(interface_name)
                if interface:
                    success = interface.reconfigure(**parameters)
                    return jsonify({
                        'success': success,
                        'interface': interface_name,
                        'parameters': interface.config.parameters
                    })

                return jsonify({'error': 'Interface not found'}), 404
                
        # Register the remaining routes
        self._register_route('/devices/batch', 'batch_operation', batch_operation, methods=['POST'])
        self._register_route('/devices/<device_id>/parameters', 'device_parameters', 
                           device_parameters, methods=['GET', 'PUT'])

    def _scan_i2c_devices(self):
        """Scan for I2C devices"""
        from devint.interfaces.i2c import I2CInterface
        from devint.base.interface import InterfaceConfig

        results = []
        for bus in [0, 1]:  # Scan common I2C buses
            try:
                config = InterfaceConfig(
                    port=f"/dev/i2c-{bus}",
                    protocol="i2c",
                    parameters={'bus': bus}
                )
                interface = I2CInterface(f"i2c_scan_{bus}", config)

                if interface.connect():
                    addresses = interface.scan()
                    for addr in addresses:
                        results.append({
                            'interface': 'i2c',
                            'bus': bus,
                            'address': f"0x{addr:02X}",
                            'address_dec': addr
                        })
                    interface.disconnect()
            except Exception as e:
                self.logger.error(f"Error scanning I2C bus {bus}: {e}")

        return jsonify({'devices': results})

    def _scan_serial_devices(self, data):
        """Scan for serial/Modbus devices"""
        from devint import auto_detect_modbus_port

        ports = data.get('ports', [])
        baudrates = data.get('baudrates', [9600, 19200, 38400, 115200])

        results = []
        for port in ports:
            for baudrate in baudrates:
                result = auto_detect_modbus_port([baudrate], debug=True)
                if result:
                    results.append({
                        'interface': 'serial',
                        'port': result['port'],
                        'baudrate': result['baudrate'],
                        'protocol': 'modbus_rtu'
                    })

        return jsonify({'devices': results})