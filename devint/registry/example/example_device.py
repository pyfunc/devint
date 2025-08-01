"""
Example device implementation for demonstration purposes.
This device simulates a simple I/O device with digital and analog channels.
"""
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum, auto

from devint.base.device import BaseDevice
from devint.base.interface import BaseInterface, InterfaceConfig
from devint.base.register import BaseRegister, RegisterType

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
    
    def initialize(self):
        """Initialize the device and its resources."""
        try:
            logger.info(f"Initializing device {self.device_id} with config: {self.config}")
            logger.info(f"Device registers: {list(self.registers.keys())}")
            
            # Initialize any required resources here
            self._initialized = True
            
            logger.info(f"Successfully initialized {self.device_id} with {len(self.config.channels)} channels")
            return True
        except Exception as e:
            logger.error(f"Error initializing device {self.device_id}: {e}", exc_info=True)
            self._initialized = False
            return False
    
    def __init__(self, config: ExampleDeviceConfig):
        """Initialize the example device with the given configuration"""
        super().__init__(device_id=config.device_id, name=f"ExampleDevice-{config.device_id}")
        self.config = config
        self._channel_values = {name: 0 for name in config.channels}
        self._sample_rate = config.sample_rate
        self._resolution = 2 ** config.resolution_bits - 1
        self._initialized = False
        
        # Set up device identity
        self.identity.manufacturer = "Example Inc."
        self.identity.model = "Example Device"
        self.identity.firmware_version = "1.0.0"
        self.identity.hardware_version = "1.0"
        
        # Set up registers for each channel
        self.registers = {}
        for name, chan_type in config.channels.items():
            # Determine register type based on channel type
            if 'IN' in chan_type.name:
                reg_type = RegisterType.INPUT_REGISTER if 'ANALOG' in chan_type.name else RegisterType.DISCRETE_INPUT
                access = 'r'  # Read-only for inputs
            else:
                reg_type = RegisterType.HOLDING_REGISTER if 'ANALOG' in chan_type.name else RegisterType.COIL
                access = 'rw'  # Read-write for outputs
                
            # Calculate scale and offset based on resolution and expected range
            max_val = self._resolution if 'ANALOG' in chan_type.name else 1
            scale = 10.0 / max_val if 'ANALOG' in chan_type.name else 1.0
            
            self.registers[name] = BaseRegister(
                name=name,
                address=len(self.registers),
                description=f"{chan_type.name} for channel {name}",
                register_type=reg_type,
                data_type="float32" if 'ANALOG' in chan_type.name else "bool",
                access=access,
                unit="V" if 'ANALOG' in chan_type.name else None,
                scale=scale,
                offset=0.0
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
    
    def get_registers(self) -> Dict[str, BaseRegister]:
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
