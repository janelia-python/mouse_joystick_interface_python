mouse_joystick_interface_python
===============================

This Python package creates a class named MouseJoystickInterface.

Authors::

    Peter Polidoro <polidorop@janelia.hhmi.org>

License::

    BSD

Example Usage::

    dev = MouseJoystickInterface() # Might automatically find devices if available
    # if devices not found automatically, specify ports directly
    dev = MouseJoystickInterface(use_ports=['/dev/ttyACM0','/dev/ttyACM0']) # Linux specific ports
    dev = MouseJoystickInterface(use_ports=['/dev/tty.usbmodem262471','/dev/tty.usbmodem262472']) # Mac OS X specific ports
    dev = MouseJoystickInterface(use_ports=['COM3','COM4']) # Windows specific ports
    dev.abort_assay()
    dev.start_assay()

    dev.mouse_joystick_controller.set_properties_to_defaults(['ALL'])
    dev.mouse_joystick_controller.get_property_values(['ALL'])
    dev.mouse_joystick_controller.reach_position1_means('getValue')
    dev.mouse_joystick_controller.reach_position1_means('setValue',[100,160,200])
    dev.mouse_joystick_controller.reach_position1_means('setArrayLength',2)
    dev.mouse_joystick_controller.reach_position1_means('setValue',[100,200])
    dev.mouse_joystick_controller.trial_count('setValue',3)
    dev.mouse_joystick_controller.repeat_aborted_trial('setValue',False)

    dev.encoder_interface.set_properties_to_defaults(['ALL'])
    dev.encoder_interface.get_property_values(['ALL'])
    dev.encoder_interface.sample_period('setValue',15)
