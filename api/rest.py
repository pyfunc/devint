# api/rest.py - rozszerzenie istniejącego API
from devices.device_manager import DeviceManager
from devices.registry.waveshare import WaveshareIO8CH

# Inicjalizacja managera urządzeń
device_manager = DeviceManager()
device_manager.register_device_type("WaveshareIO8CH", WaveshareIO8CH)


@app.route('/devices', methods=['GET'])
def list_devices():
    """Lista wszystkich urządzeń"""
    return jsonify({
        'devices': [
            device.to_dict()
            for device in device_manager.devices.values()
        ]
    })


@app.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id: str):
    """Pobierz szczegóły urządzenia"""
    device = device_manager.get_device(device_id)
    if device:
        return jsonify(device.to_dict())
    return jsonify({'error': 'Device not found'}), 404


@app.route('/devices/<device_id>/registers/<register_name>', methods=['GET', 'PUT'])
def device_register(device_id: str, register_name: str):
    """Operacje na rejestrach urządzenia"""
    device = device_manager.get_device(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404

    if request.method == 'GET':
        value = device.read_register(register_name)
        return jsonify({
            'device_id': device_id,
            'register': register_name,
            'value': value
        })
    else:  # PUT
        data = request.get_json()
        success = device.write_register(register_name, data.get('value'))
        return jsonify({
            'success': success,
            'device_id': device_id,
            'register': register_name
        })