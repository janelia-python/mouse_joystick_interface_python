from __future__ import print_function, division
import time
import atexit
import os

from modular_client import ModularClients

try:
    from pkg_resources import get_distribution, DistributionNotFound
    _dist = get_distribution('mouse_joystick_interface')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'mouse_joystick_interface')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except (ImportError,DistributionNotFound):
    __version__ = None
else:
    __version__ = _dist.version


DEBUG = False

class MouseJoystickInterface(object):
    '''
    MouseJoystickInterface.

    Example Usage:

    dev = MouseJoystickInterface() # Might automatically find device if one available
    # if it is not found automatically, specify port directly
    dev = MouseJoystickInterface(port='/dev/ttyACM0') # Linux specific port
    dev = MouseJoystickInterface(port='/dev/tty.usbmodem262471') # Mac OS X specific port
    dev = MouseJoystickInterface(port='COM3') # Windows specific port

    '''

    def __init__(self,*args,**kwargs):
        t_start = time.time()
        self._modular_clients = ModularClients(*args,**kwargs)
        atexit.register(self._exit_mouse_joystick_interface)
        t_end = time.time()
        self._debug_print('Initialization time =', (t_end - t_start))

    def _exit_mouse_joystick_interface(self):
        pass

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':

    debug = False
    dev = MouseJoystickInterface(debug=debug)
