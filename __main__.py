#!/usr/bin/env python3
"""
Main entry point for the devint application.
"""
import sys
from devint.services.multi_service import MultiDeviceService

def main():
    """Run the multi-device service."""
    try:
        service = MultiDeviceService(port=5000)
        print(f"Starting MultiDeviceService on port {service.port}")
        service.start(host='0.0.0.0', debug=True)
        
        # Keep the main thread alive
        while True:
            try:
                pass
            except KeyboardInterrupt:
                print("\nShutting down...")
                service.stop()
                sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
