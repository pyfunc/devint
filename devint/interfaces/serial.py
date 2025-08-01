"""
Serial interface implementation for device communication.
"""
import time
import serial
from typing import Optional, Union, List, Dict, Any

from devint.base.interface import BaseInterface, InterfaceConfig


class SerialInterface(BaseInterface):
    """
    Serial interface implementation using pyserial.
    
    This class provides a serial communication interface for devices that
    use serial ports for communication.
    """
    
    def __init__(self, config: Optional[InterfaceConfig] = None):
        """
        Initialize the serial interface.
        
        Args:
            config: Optional configuration for the interface.
                   If not provided, default values will be used.
        """
        default_config = InterfaceConfig(
            name="serial",
            params={
                "port": "/dev/ttyUSB0",
                "baudrate": 9600,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1,
                "timeout": 1.0,
                "xonxoff": False,
                "rtscts": False,
                "dsrdtr": False,
                "write_timeout": None,
                "inter_byte_timeout": None
            }
        )
        
        # Merge with provided config
        if config:
            default_config.params.update(config.params)
            
        super().__init__(default_config)
        self._serial: Optional[serial.Serial] = None
    
    def connect(self) -> bool:
        """
        Connect to the serial port.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        if self._serial and self._serial.is_open:
            return True
            
        try:
            self._serial = serial.Serial(
                port=self.config.params["port"],
                baudrate=self.config.params["baudrate"],
                bytesize=self.config.params["bytesize"],
                parity=self.config.params["parity"],
                stopbits=self.config.params["stopbits"],
                timeout=self.config.params["timeout"],
                xonxoff=self.config.params["xonxoff"],
                rtscts=self.config.params["rtscts"],
                dsrdtr=self.config.params["dsrdtr"],
                write_timeout=self.config.params["write_timeout"],
                inter_byte_timeout=self.config.params["inter_byte_timeout"]
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to serial port: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close the serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            self._serial = None
    
    def read(self, size: int = 1) -> bytes:
        """
        Read data from the serial port.
        
        Args:
            size: Number of bytes to read.
            
        Returns:
            bytes: The data read from the serial port.
        """
        if not self._serial or not self._serial.is_open:
            if not self.connect():
                raise IOError("Serial port is not connected")
                
        return self._serial.read(size)
    
    def write(self, data: bytes) -> int:
        """
        Write data to the serial port.
        
        Args:
            data: Data to write to the serial port.
            
        Returns:
            int: Number of bytes written.
        """
        if not self._serial or not self._serial.is_open:
            if not self.connect():
                raise IOError("Serial port is not connected")
                
        return self._serial.write(data)
    
    def flush(self) -> None:
        """Flush the serial port buffers."""
        if self._serial and self._serial.is_open:
            self._serial.flush()
    
    def available_ports(self) -> List[str]:
        """
        Get a list of available serial ports.
        
        Returns:
            List[str]: List of available serial port names.
        """
        import serial.tools.list_ports
        return [port.device for port in serial.tools.list_ports.comports()]
    
    def __del__(self):
        """Ensure the serial connection is closed when the object is destroyed."""
        self.disconnect()