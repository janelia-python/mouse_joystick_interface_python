from __future__ import print_function, division
import time
import atexit
import os
from datetime import datetime
from threading import Timer

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

class MouseJoystickInterface():
    '''
    MouseJoystickInterface.

    Example Usage:

    dev = MouseJoystickInterface() # Might automatically find device if one available
    # if it is not found automatically, specify port directly
    dev = MouseJoystickInterface(port='/dev/ttyACM0') # Linux specific port
    dev = MouseJoystickInterface(port='/dev/tty.usbmodem262471') # Mac OS X specific port
    dev = MouseJoystickInterface(port='COM3') # Windows specific port

    '''

    _CHECK_FOR_DATA_PERIOD = 4.0

    def __init__(self,*args,**kwargs):
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            kwargs.update({'debug': DEBUG})
            self.debug = DEBUG
            self._save_path = os.path.expanduser('~/mouse_joystick')
        if not os.path.exists(self._save_path):
            os.makedirs(self._save_path)
        t_start = time.time()
        self._check_for_data_timer = PerpetualTimer(self._CHECK_FOR_DATA_PERIOD,self._check_for_data)
        atexit.register(self._exit_mouse_joystick_interface)
        self._modular_clients = ModularClients(*args,**kwargs)
        mjc_name = 'mouse_joystick_controller'
        mjc_form_factor = '5x3'
        mjc_serial_number = 0
        if (mjc_name not in self._modular_clients):
            raise RuntimeError(mjc_name + ' is not connected!')
        self.mouse_joystick_controller = self._modular_clients[mjc_name][mjc_form_factor][mjc_serial_number]
        ei_name = 'encoder_interface_simple'
        ei_form_factor = '3x2'
        ei_serial_number = 0
        if (ei_name not in self._modular_clients):
            raise RuntimeError(ei_name + ' is not connected!')
        self.encoder_interface = self._modular_clients[ei_name][ei_form_factor][ei_serial_number]
        t_end = time.time()
        self._debug_print('Initialization time =', (t_end - t_start))

    def start_assay(self):
        status = self.mouse_joystick_controller.get_assay_status()
        if (status['state'] != 'ASSAY_FINISHED') and (status['state'] != 'ASSAY_NOT_STARTED'):
            self.abort_assay()
            while True:
                time.sleep(self._CHECK_FOR_DATA_PERIOD)
                status = self.mouse_joystick_controller.get_assay_status()
                if (status['state'] == 'ASSAY_FINISHED'):
                    break

        self.mouse_joystick_controller.set_time(time.time())
        self.encoder_interface.set_time(time.time())
        self.mouse_joystick_controller.start_assay()
        self._check_for_data_timer.start()

    def abort_assay(self):
        self._check_for_data_timer.cancel()
        self.mouse_joystick_controller.abort_assay()

    def _debug_print(self, *args):
        if self.debug:
            print(*args)

    def _exit_mouse_joystick_interface(self):
        self._check_for_data_timer.cancel()
        self.mouse_joystick_controller.abort_assay()

    def _get_date_str(self):
        d = datetime.fromtimestamp(time.time())
        date_str = d.strftime("%Y%m%d")
        return date_str

    def _get_date_time_str(self):
        d = datetime.fromtimestamp(time.time())
        date_time_str = d.strftime("%Y%m%d_%H%M%S")
        return date_time_str

    def _check_for_data(self):
        status = self.mouse_joystick_controller.get_assay_status()
        unread_trial_data = status.pop('unread_trial_data')
        state = status.pop('state')
        if unread_trial_data:
            print(status)
            encoder_samples = self.encoder_interface.get_samples()
            print(len(encoder_samples))
            trial_data = self.mouse_joystick_controller.read_trial_data()
            print(trial_data)
            self.mouse_joystick_controller.set_time(time.time())
            self.encoder_interface.set_time(time.time())
        if state == 'ASSAY_FINISHED':
            self._check_for_data_timer.cancel()

class PerpetualTimer():

   def __init__(self,t,h_function):
       self.t = t
       self.h_function = h_function
       self.thread = Timer(self.t,self.handle_function)
       self.enabled = False

   def handle_function(self):
       if self.enabled:
           self.h_function()
           self.thread = Timer(self.t,self.handle_function)
           self.thread.start()

   def start(self):
       self.enabled = True
       self.thread.start()

   def cancel(self):
       self.enabled = False
       self.thread.cancel()

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':

    debug = False
    dev = MouseJoystickInterface(debug=debug)
