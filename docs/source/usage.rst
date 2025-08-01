Usage
=====

Quick Start
-----------

Here's a quick example to get you started with devint:

.. code-block:: python

    from devint import MultiDeviceService
    from devint.registry.raspberry_pi.sense_hat import RaspberrySenseHAT

    # Initialize the service
    service = MultiDeviceService(port=5000)

    # Add a device
    sense_hat = RaspberrySenseHAT("sense_hat_1")
    service.add_device(sense_hat)

    # Start the service (includes web interface on port 5000)
    service.start()

Basic Concepts
--------------

Devices
~~~~~~~
Devices represent physical hardware components. Each device has:

- A unique identifier
- A set of capabilities
- One or more interfaces for communication
- Registers for data storage and retrieval

Interfaces
~~~~~~~~~~
Interfaces handle communication with devices. Supported interfaces include:

- I2C
- SPI
- GPIO
- Serial
- TCP/UDP
- CAN bus
- 1-Wire

Registers
~~~~~~~~~
Registers store device data and configuration. They can be:

- Read-only or read-write
- Different data types (bool, int, float, string, etc.)
- Organized in a hierarchical structure

Services
~~~~~~~~
Services provide higher-level functionality:

- Device discovery
- Web interface
- REST API
- MQTT integration

Examples
--------

Using a Raspberry Pi Sense HAT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from devint import MultiDeviceService
    from devint.registry.raspberry_pi.sense_hat import RaspberrySenseHAT

    # Initialize service
    service = MultiDeviceService(port=5000)
    
    # Add Sense HAT
    sense_hat = RaspberrySenseHAT("my_sense_hat")
    service.add_device(sense_hat)
    
    # Start the service
    service.start()

Using a Waveshare 8-Channel I/O Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from devint import MultiDeviceService
    from devint.registry.waveshare.io_8ch import WaveshareIO8CH

    # Initialize service
    service = MultiDeviceService(port=5000)
    
    # Add Waveshare I/O module
    io_module = WaveshareIO8CH("io_module_1", 
                             port="/dev/ttyUSB0", 
                             baudrate=9600,
                             address=1)
    service.add_device(io_module)
    
    # Start the service
    service.start()

Web Interface
-------------
After starting a service, you can access the web interface at:

.. code-block:: text

    http://localhost:5000

The web interface allows you to:

- View connected devices
- Monitor device status
- Read and write registers
- View logs and diagnostics
