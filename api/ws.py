from flask import Flask, render_template, send_from_directory
from .ws import WebSocketAPI


def create_rest_app(...):
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # ... existing code ...

    # Add WebSocket support
    ws_api = WebSocketAPI(app, device_manager)

    # Add routes for web interface
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/serial/ports')
    def get_serial_ports():
        from modapi.api.rtu import find_serial_ports
        ports = find_serial_ports()
        return jsonify({'ports': ports})

    # Use WebSocket-enabled run method
    def run_with_websocket(host='0.0.0.0', port=5000, debug=False):
        ws_api.run(host=host, port=port, debug=debug)

    app.run = run_with_websocket

    return app