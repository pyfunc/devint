#!/usr/bin/env python3
"""
Web-based demonstration of ModbusRTUDevice functionality.

This script creates a Flask web server that allows:
1. Viewing device status
2. Reading registers
3. Writing to registers
4. Testing various register types
"""

import sys
import logging
from typing import Any, Union, cast
from flask import Flask, render_template_string, request, jsonify, Response, Blueprint

# Add the project root to the Python path
sys.path.append('/home/tom/github/pyfunc/devint')

from devint.registry.modbus.rtu_device import ModbusRTUDevice
from devint.services.multi_service import MultiDeviceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app with a unique name to avoid conflicts
app = Flask("modbus_rtu_web_demo")

# Create a Blueprint to avoid route conflicts when running all examples together
modbus_blueprint = Blueprint('modbus_web_demo', __name__, url_prefix='/modbus_demo')

# Don't create a MultiDeviceService to avoid endpoint conflicts
# service = MultiDeviceService()

# Create a ModbusRTUDevice in mock mode
modbus_device = ModbusRTUDevice(
    device_id="modbus_rtu_web_demo",
    port="/dev/ttyACM0",
    baudrate=9600,
    unit_id=1,
    mock_mode=True  # Use mock mode for demo
)

# No need to add device to service since we're not using MultiDeviceService
# service.add_device(modbus_device)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ModbusRTU Device Demo</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2 {
            color: #333;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .result {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
        }
        .success {
            background-color: #dff0d8;
            color: #3c763d;
        }
        .error {
            background-color: #f2dede;
            color: #a94442;
        }
    </style>
</head>
<body>
    <h1>ModbusRTU Device Web Demo</h1>
    
    <div class="card">
        <h2>Device Status</h2>
        <p><strong>Device ID:</strong> {{ device.device_id }}</p>
        <p><strong>Port:</strong> {{ device.port }}</p>
        <p><strong>Baudrate:</strong> {{ device.baudrate }}</p>
        <p><strong>Unit ID:</strong> {{ device.unit_id }}</p>
        <p><strong>Connected:</strong> {{ "Yes" if device.connected else "No" }}</p>
        <p><strong>Mock Mode:</strong> {{ "Yes" if device.mock_mode else "No" }}</p>
    </div>
    
    <div class="card">
        <h2>Read Register</h2>
        <div class="form-group">
            <label for="read-register">Register Name:</label>
            <input type="text" id="read-register" placeholder="e.g., coil_0, holding_10">
        </div>
        <button onclick="readRegister()">Read</button>
        <div id="read-result" class="result"></div>
    </div>
    
    <div class="card">
        <h2>Write Register</h2>
        <div class="form-group">
            <label for="write-register">Register Name:</label>
            <input type="text" id="write-register" placeholder="e.g., coil_0, holding_10">
        </div>
        <div class="form-group">
            <label for="write-value">Value:</label>
            <input type="text" id="write-value" placeholder="true, false, or integer value">
        </div>
        <button onclick="writeRegister()">Write</button>
        <div id="write-result" class="result"></div>
    </div>
    
    <div class="card">
        <h2>Quick Tests</h2>
        <button onclick="testCoil()">Test Coil</button>
        <button onclick="testHolding()">Test Holding Register</button>
        <button onclick="testInput()">Test Input Register</button>
        <button onclick="testDiscrete()">Test Discrete Input</button>
        <div id="test-result" class="result"></div>
    </div>
    
    <div class="card">
        <h2>Device State</h2>
        <button onclick="getDeviceState()">Get Device State</button>
        <pre id="device-state"></pre>
    </div>
    
    <script>
        function readRegister() {
            const register = document.getElementById('read-register').value;
            fetch(`/api/read?register=${register}`)
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('read-result');
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.textContent = `Value: ${data.value}`;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = `Error: ${data.error}`;
                    }
                });
        }
        
        function writeRegister() {
            const register = document.getElementById('write-register').value;
            const value = document.getElementById('write-value').value;
            fetch('/api/write', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ register, value }),
            })
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('write-result');
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.textContent = 'Write successful';
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = `Error: ${data.error}`;
                    }
                });
        }
        
        function testCoil() {
            fetch('/api/test/coil')
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('test-result');
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.textContent = `Test successful: ${JSON.stringify(data.result)}`;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = `Error: ${data.error}`;
                    }
                });
        }
        
        function testHolding() {
            fetch('/api/test/holding')
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('test-result');
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.textContent = `Test successful: ${JSON.stringify(data.result)}`;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = `Error: ${data.error}`;
                    }
                });
        }
        
        function testInput() {
            fetch('/api/test/input')
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('test-result');
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.textContent = `Test successful: ${JSON.stringify(data.result)}`;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = `Error: ${data.error}`;
                    }
                });
        }
        
        function testDiscrete() {
            fetch('/api/test/discrete')
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('test-result');
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.textContent = `Test successful: ${JSON.stringify(data.result)}`;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = `Error: ${data.error}`;
                    }
                });
        }
        
        function getDeviceState() {
            fetch('/api/state')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('device-state').textContent = JSON.stringify(data, null, 2);
                });
        }
    </script>
</body>
</html>
"""

@modbus_blueprint.route('/')
def index() -> str:
    """Render the main page."""
    return cast(str, render_template_string(HTML_TEMPLATE, device=modbus_device))

@modbus_blueprint.route('/api/read')
def read_register() -> Response:
    """API endpoint to read a register."""
    register_name = request.args.get('register', '')
    if not register_name:
        return jsonify({'success': False, 'error': 'Register name is required'})
    
    try:
        value = modbus_device.read_register(register_name)
        if value is None:
            return jsonify({'success': False, 'error': 'Failed to read register'})
        return jsonify({'success': True, 'value': value})
    except Exception as e:
        logger.error(f"Error reading register: {e}")
        return jsonify({'success': False, 'error': str(e)})

@modbus_blueprint.route('/api/write', methods=['POST'])
def write_register() -> Response:
    """API endpoint to write to a register."""
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'})
        
    register_name = data.get('register', '')
    value_str = data.get('value', '')
    
    if not register_name:
        return jsonify({'success': False, 'error': 'Register name is required'})
    
    if not value_str:
        return jsonify({'success': False, 'error': 'Value is required'})
    
    # Convert value to appropriate type
    try:
        if isinstance(value_str, str):
            if value_str.lower() == 'true':
                value: Any = True
            elif value_str.lower() == 'false':
                value = False
            else:
                try:
                    value = int(value_str)
                except ValueError:
                    try:
                        value = float(value_str)
                    except ValueError:
                        value = value_str
        else:
            value = value_str
        
        result = modbus_device.write_register(register_name, value)
        if not result:
            return jsonify({'success': False, 'error': 'Failed to write register'})
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error writing register: {e}")
        return jsonify({'success': False, 'error': str(e)})

@modbus_blueprint.route('/api/test/coil')
def test_coil() -> Response:
    """Test coil read/write."""
    try:
        # Write to coil
        write_result = modbus_device.write_register('coil_100', True)
        # Read back
        read_result = modbus_device.read_register('coil_100')
        
        return jsonify({
            'success': True,
            'write_result': write_result,
            'read_result': read_result,
            'consistent': read_result is True
        })
    except Exception as e:
        logger.error(f"Error testing coil: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@modbus_blueprint.route('/api/test/holding')
def test_holding() -> Response:
    """Test holding register read/write."""
    try:
        # Write to holding register
        test_value = 12345
        write_result = modbus_device.write_register('holding_200', test_value)
        # Read back
        read_result = modbus_device.read_register('holding_200')
        
        return jsonify({
            'success': True,
            'write_result': write_result,
            'read_result': read_result,
            'test_value': test_value,
            'consistent': read_result == test_value
        })
    except Exception as e:
        logger.error(f"Error testing holding register: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@modbus_blueprint.route('/api/test/input')
def test_input() -> Response:
    """Test input register read."""
    try:
        # Read from input register
        read_result = modbus_device.read_register('input_300')
        
        return jsonify({
            'success': True,
            'read_result': read_result
        })
    except Exception as e:
        logger.error(f"Error testing input register: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@modbus_blueprint.route('/api/test/discrete')
def test_discrete() -> Response:
    """Test discrete input read."""
    try:
        # Read from discrete input
        read_result = modbus_device.read_register('discrete_400')
        
        return jsonify({
            'success': True,
            'read_result': read_result
        })
    except Exception as e:
        logger.error(f"Error testing discrete input: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@modbus_blueprint.route('/api/state')
def get_state() -> Response:
    """Get device state."""
    try:
        # Get device state
        state = modbus_device.dump_state()
        
        return jsonify({
            'success': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error getting device state: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Register the blueprint with the Flask app after all routes are defined
app.register_blueprint(modbus_blueprint)

if __name__ == "__main__":
    # Run the Flask app
    try:
        # Use a different port to avoid conflicts with the main service
        print(f"Starting Modbus RTU Web Demo on http://0.0.0.0:5002/")
        print("Press Ctrl+C to stop")
        app.run(host="0.0.0.0", port=5002, debug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        logger.info("Shutting down device")
        modbus_device.shutdown()
        # No need to remove device from service since we're not using MultiDeviceService
        # logger.info("Removing device from service")
        # service.remove_device(modbus_device.device_id)
