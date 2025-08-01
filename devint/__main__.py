#!/usr/bin/env python3
"""
DevInt Command Line Interface

This module provides the command-line interface for the DevInt package.
"""

import argparse
import logging
import sys
from typing import List, Optional

from devint import __version__
from devint.services.multi_service import MultiDeviceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: List of command line arguments
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='DevInt - Unified Device Interface',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'DevInt {__version__}',
        help='Show version and exit'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # List devices command
    list_parser = subparsers.add_parser('list', help='List available devices')
    
    # Run service command
    run_parser = subparsers.add_parser('run', help='Run the device service')
    run_parser.add_argument(
        '-p', '--port',
        type=int,
        default=5000,
        help='Port to run the service on'
    )
    run_parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind the service to'
    )
    
    # Device-specific commands
    device_parser = subparsers.add_parser('device', help='Device management')
    device_subparsers = device_parser.add_subparsers(dest='device_command', help='Device command')
    
    # Add device command
    add_parser = device_subparsers.add_parser('add', help='Add a device')
    add_parser.add_argument('type', help='Device type')
    add_parser.add_argument('--id', required=True, help='Device ID')
    add_parser.add_argument('--name', help='Device name')
    add_parser.add_argument('--port', help='Device port')
    
    # Remove device command
    remove_parser = device_subparsers.add_parser('remove', help='Remove a device')
    remove_parser.add_argument('device_id', help='Device ID to remove')
    
    # List devices command
    device_subparsers.add_parser('list', help='List all devices')
    
    # Test device command
    test_parser = device_subparsers.add_parser('test', help='Test a device')
    test_parser.add_argument('device_id', help='Device ID to test')
    
    return parser.parse_args(args)

def list_devices() -> None:
    """List all available devices."""
    print("Available devices:")
    # TODO: Implement device discovery
    print("No device discovery implemented yet")

def run_service(host: str, port: int) -> None:
    """Run the device service.
    
    Args:
        host: Host to bind to
        port: Port to listen on
    """
    try:
        service = MultiDeviceService()
        print(f"Starting DevInt service on http://{host}:{port}")
        print("Press Ctrl+C to stop")
        service.run(host=host, port=port)
    except KeyboardInterrupt:
        print("\nShutting down...")
        service.shutdown()
    except Exception as e:
        logger.error(f"Error running service: {e}")
        sys.exit(1)

def handle_device_command(args: argparse.Namespace) -> None:
    """Handle device-related commands.
    
    Args:
        args: Parsed command line arguments
    """
    service = MultiDeviceService()
    
    if args.device_command == 'add':
        print(f"Adding {args.type} device with ID {args.id}")
        # TODO: Implement device addition
        print("Device addition not implemented yet")
        
    elif args.device_command == 'remove':
        print(f"Removing device {args.device_id}")
        # TODO: Implement device removal
        print("Device removal not implemented yet")
        
    elif args.device_command == 'list':
        devices = service.get_devices()
        if not devices:
            print("No devices configured")
        else:
            print("Configured devices:")
            for device_id, device in devices.items():
                print(f"- {device_id}: {device.name} ({device.__class__.__name__})")
    
    elif args.device_command == 'test':
        print(f"Testing device {args.device_id}")
        # TODO: Implement device testing
        print("Device testing not implemented yet")

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the devint command line interface.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parse_args(args)
    
    # Set up logging
    log_level = logging.DEBUG if parsed_args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        if parsed_args.command == 'list':
            list_devices()
        elif parsed_args.command == 'run':
            run_service(parsed_args.host, parsed_args.port)
        elif parsed_args.command == 'device':
            handle_device_command(parsed_args)
        else:
            # No command provided, show help
            parse_args(['--help'])
            
    except Exception as e:
        logger.error(f"Error: {e}")
        if parsed_args.debug:
            logger.exception("Detailed error:")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
