"""
Example device implementation for demonstration purposes.
This device simulates a simple I/O device with digital and analog channels.
"""
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum, auto

from devint.base.device import BaseDevice
from devint.base.interface import DeviceInterface, InterfaceConfig
from devint.base.register import Register, RegisterType

logger = logging.getLogger(__name__)

class ChannelType(Enum):
    """Types of channels supported by the example device"""
    DIGITAL_IN = auto()
    DIGITAL_OUT = auto()
    ANALOG_IN = auto()
    ANALOG_OUT = auto()

@dataclass
class ExampleDeviceConfig:
    """Configuration for the example device"""
    device_id: str
    channels: Dict[str, ChannelType] = field(default_factory=dict)
    sample_rate: float = 1.0  # Hz
    resolution_bits: int = 12

class ExampleDevice(BaseDevice):
    """
    Example device implementation that demonstrates various capabilities
    including digital and analog I/O operations.
    """
    
    def __init__(self, config: ExampleDeviceConfig):
        """Initialize the example device with the given configuration"""
        super().__init__(config.device_id)
        self.config = config
        self._channel_values = {name: 0 for name in config.channels}
        self._sample_rate = config.sample_rate
        self._resolution = 2 ** config.resolution_bits - 1
        
        # Set up registers for each channel
        self.registers = {}
        for name, chan_type in config.channels.items():
            reg_type = RegisterType.READ_ONLY if 'IN' in chan_type.name else RegisterType.READ_WRITE
            self.registers[name] = Register(
                name=name,
                address=len(self.registers),
                description=f"{chan_type.name} for channel {name}",
                register_type=reg_type,
                value_range=(0, self._resolution) if 'ANALOG' in chan_type.name else (0, 1)
            )
    
    def read_register(self, register_name: str) -> Union[int, float]:
        """Read the value of a register"""
        if register_name not in self.registers:
            raise ValueError(f"Unknown register: {register_name}")
            
        reg = self.registers[register_name]
        
        # For input channels, generate a simulated value
        if 'IN' in reg.description:
            if 'ANALOG' in reg.description:
                # Simulate an analog input with some noise
                import random
                value = int(self._resolution * 0.5 * (1 + 0.1 * random.random()))
            else:
                # Simulate a digital input that toggles
                value = 1 if self._channel_values.get(register_name, 0) == 0 else 0
            self._channel_values[register_name] = value
            return value
            
        # For output channels, return the current value
        return self._channel_values.get(register_name, 0)
    
    def write_register(self, register_name: str, value: Union[int, float]) -> bool:
        """Write a value to a register"""
        if register_name not in self.registers:
            raise ValueError(f"Unknown register: {register_name}")
            
        reg = self.registers[register_name]
        
        # Check if register is writable
        if reg.register_type == RegisterType.READ_ONLY:
            raise PermissionError(f"Register {register_name} is read-only")
            
        # Validate value range
        min_val, max_val = reg.value_range
        if not (min_val <= value <= max_val):
            raise ValueError(f"Value {value} out of range [{min_val}, {max_val}] for register {register_name}")
            
        # Store the value
        self._channel_values[register_name] = int(value)
        logger.info(f"Set {register_name} = {value}")
        return True
    
    def get_registers(self) -> Dict[str, Register]:
        """Get all registers for this device"""
        return self.registers
        
    def get_info(self) -> Dict[str, Any]:
        """Get device information"""
        return {
            'device_id': self.device_id,
            'type': 'ExampleDevice',
            'channels': {name: chan_type.name for name, chan_type in self.config.channels.items()},
            'sample_rate': self._sample_rate,
            'resolution_bits': self.config.resolution_bits
        }

# Example factory function to create an instance
def create_example_device(device_id: str = "example-1") -> ExampleDevice:
    """Create an example device with some default channels"""
    config = ExampleDeviceConfig(
        device_id=device_id,
        channels={
            'dio0': ChannelType.DIGITAL_IN,
            'dio1': ChannelType.DIGITAL_OUT,
            'ain0': ChannelType.ANALOG_IN,
            'aout0': ChannelType.ANALOG_OUT
        },
        sample_rate=10.0,
        resolution_bits=12
    )
    return ExampleDevice(config)
