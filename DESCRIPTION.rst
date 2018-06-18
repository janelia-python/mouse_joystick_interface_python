mouse_joystick_interface_python
===============================

This Python package creates a class named MouseJoystickInterface.

Authors::

    Peter Polidoro <polidorop@janelia.hhmi.org>

License::

    BSD

Example Usage::

    from mouse_joystick_interface import MouseJoystickInterface
    dev = MouseJoystickInterface() # Might automatically find device if one available
    # if it is not found automatically, specify port directly
    dev = MouseJoystickInterface(port='/dev/ttyACM0') # Linux specific port
    dev = MouseJoystickInterface(port='/dev/tty.usbmodem262471') # Mac OS X specific port
    dev = MouseJoystickInterface(port='COM3') # Windows specific port
