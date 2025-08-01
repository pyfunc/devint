"""
Example script to demonstrate using the ExampleDevice with the web interface.
This script starts the web server and adds an example device that can be controlled via HTTP.
"""
import sys
import time
import requests
from devint.services.multi_service import MultiDeviceService
from devint.registry.example import create_example_device

def main():
    # Create and start the web service
    service = MultiDeviceService(port=5001)
    
    # Create an example device
    device = create_example_device("example-1")
    
    # Add the device to the service
    if not service.add_device(device):
        print(f"Failed to add device {device.device_id} to the service")
        return
    
    # Start the service in a background thread
    import threading
    server_thread = threading.Thread(target=service.run, kwargs={'debug': False})
    server_thread.daemon = True
    server_thread.start()
    
    try:
        print(f"Web interface running at http://localhost:{service.port}")
        print("Example device endpoints:")
        print(f"  - GET /devices/{device.device_id} - Get device info")
        print(f"  - GET /devices/{device.device_id}/registers/dio0 - Read digital input")
        print(f"  - GET /devices/{device.device_id}/registers/dio1 - Read digital output")
        print(f"  - POST /devices/{device.device_id}/registers/dio1 - Write digital output (body: {{\"value\": 1}})")
        print(f"  - GET /devices/{device.device_id}/registers/ain0 - Read analog input")
        print(f"  - GET /devices/{device.device_id}/registers/aout0 - Read analog output")
        print(f"  - POST /devices/{device.device_id}/registers/aout0 - Write analog output (body: {{\"value\": 2048}})")
        print("\nPress Ctrl+C to stop")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        service.shutdown()
        server_thread.join(timeout=2)

if __name__ == "__main__":
    main()
