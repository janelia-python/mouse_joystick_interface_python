from __future__ import print_function, division
import time
import atexit
import os
from datetime import datetime
from threading import Timer
import csv

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

    dev = MouseJoystickInterface() # Might automatically find devices if available
    # if devices not found automatically, specify ports directly
    dev = MouseJoystickInterface(use_ports=['/dev/ttyACM0','/dev/ttyACM0']) # Linux specific ports
    dev = MouseJoystickInterface(use_ports=['/dev/tty.usbmodem262471','/dev/tty.usbmodem262472']) # Mac OS X specific ports
    dev = MouseJoystickInterface(use_ports=['COM3','COM4']) # Windows specific ports
    # abort_assay prematurely stops a running assay and leaves the rig ready to start a new assay
    dev.abort_assay()
    # start_assay is the main method that starts the assay, collects assay data, and saves data files
    dev.start_assay()

    # optional mouse_joystick_controller methods
    dev.mouse_joystick_controller.set_properties_to_defaults(['ALL'])
    dev.mouse_joystick_controller.get_property_values(['ALL'])
    dev.mouse_joystick_controller.reach_position1_means('getValue')
    dev.mouse_joystick_controller.reach_position1_means('setValue',[100,160,200])
    dev.mouse_joystick_controller.reach_position1_means('setArrayLength',2)
    dev.mouse_joystick_controller.reach_position1_means('setValue',[100,200])
    dev.mouse_joystick_controller.trial_count('setValue',3)
    dev.mouse_joystick_controller.repeat_aborted_trial('setValue',False)
    dev.mouse_joystick_controller.get_assay_status()
    dev.mouse_joystick_controller.move_joystick_to_base_position()
    dev.mouse_joystick_controller.move_joystick_to_reach_position()
    count = 1
    dev.mouse_joystick_controller.activate_lickport(count)
    dev.mouse_joystick_controller.get_trial_timing_data()
    dev.mouse_joystick_controller.abort_trial()

    # optional encoder_interface methods
    dev.encoder_interface.set_properties_to_defaults(['ALL'])
    dev.encoder_interface.get_property_values(['ALL'])
    dev.encoder_interface.sample_period('setValue',15)
    dev.encoder_interface.get_positions()
    dev.encoder_interface.get_sample_count()
    dev.encoder_interface.get_samples()
    '''

    _CHECK_FOR_UNREAD_DATA_PERIOD = 4.0

    def __init__(self,*args,**kwargs):
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            kwargs.update({'debug': DEBUG})
            self.debug = DEBUG
        self._base_path = os.path.expanduser('~/mouse_joystick')
        self._args = args
        self._kwargs = kwargs
        t_start = time.time()
        atexit.register(self._exit_mouse_joystick_interface)
        self._assay_running = False
        self._trials_fieldnames = ['trial_index',
                                   'successful_trial_count',
                                   'trial',
                                   'block',
                                   'set',
                                   'reach_position_0',
                                   'reach_position_1',
                                   'pull_torque',
                                   'pull_threshold',
                                   'trial_start',
                                   'mouse_ready',
                                   'joystick_ready',
                                   'pull',
                                   'push',
                                   'timeout',
                                   'trial_abort']
        self._trial_fieldnames = ['date_time',
                                  'milliseconds',
                                  'joystick_position']
        self._setup_modular_clients()
        t_end = time.time()
        self._debug_print('Initialization time =', (t_end - t_start))

    def _setup_modular_clients(self):
        self._modular_clients = ModularClients(*self._args,**self._kwargs)
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

    def start_assay(self):
        if self._assay_running:
            print('Assay already running.')
            return

        print('Starting assay...')

        print('Setting time.')
        self.mouse_joystick_controller.set_time(int(time.time()))
        self.encoder_interface.set_time(int(time.time()))

        print('Setting up data files.')
        self._assay_path = os.path.join(self._base_path,self._get_date_time_str())
        os.makedirs(self._assay_path)
        trials_filename = 'trials.csv'
        trials_path = os.path.join(self._assay_path,trials_filename)
        self._trials_file = open(trials_path,'w')
        self._trials_writer = csv.DictWriter(self._trials_file,fieldnames=self._trials_fieldnames)
        self._trials_writer.writeheader()
        self.mouse_joystick_controller.start_assay()
        self._assay_running = True
        self._check_for_unread_data_timer = Timer(self._CHECK_FOR_UNREAD_DATA_PERIOD,self._check_for_unread_data)
        self._check_for_unread_data_timer.start()
        print('Assay running!')

    def abort_assay(self):
        self._assay_running = False
        try:
            self._trials_file.close()
        except (AttributeError,ValueError):
            pass
        try:
            self._check_for_unread_data_timer.cancel()
        except AttributeError:
            pass
        try:
            self.mouse_joystick_controller.abort_assay()
        except:
            pass

    def _debug_print(self, *args):
        if self.debug:
            print(*args)

    def _exit_mouse_joystick_interface(self):
        self.abort_assay()

    def _get_date_time_str(self,timestamp=None):
        if timestamp is None:
            d = datetime.fromtimestamp(time.time())
        elif timestamp == 0:
            date_time_str = 'NULL'
            return date_time_str
        else:
            d = datetime.fromtimestamp(timestamp)
        date_time_str = d.strftime('%Y-%m-%d-%H-%M-%S')
        return date_time_str

    def _get_time_from_date_time_str(self,date_time_str):
        if date_time_str != 'NULL':
            timestamp = time.mktime(datetime.strptime(date_time_str,'%Y-%m-%d-%H-%M-%S').timetuple())
        else:
            timestamp = 0
        return timestamp

    def _check_for_unread_data(self):
        if not self._assay_running:
            return
        status = self.mouse_joystick_controller.get_assay_status()
        unread_trial_timing_data = status.pop('unread_trial_timing_data')
        state = status.pop('state')
        if unread_trial_timing_data:
            encoder_samples = self.encoder_interface.get_samples()
            trial_filename = 'trial_{0}.csv'.format(status['trial_index'])
            trial_path = os.path.join(self._assay_path,trial_filename)
            with open(trial_path,'w') as trial_file:
                self._trial_writer = csv.writer(trial_file,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
                self._trial_writer.writerow(self._trial_fieldnames)
                for sample in encoder_samples:
                    sample[0] = self._get_date_time_str(sample[0])
                    self._trial_writer.writerow(sample)
            trial_timing_data = self.mouse_joystick_controller.get_trial_timing_data()
            trial_timing_data_date_time = {key: self._get_date_time_str(value) for (key,value) in trial_timing_data.items()}
            trial_data = {**status,**trial_timing_data_date_time}
            print('Trial data:')
            print(trial_data)
            self._trials_writer.writerow(trial_data)
            self.mouse_joystick_controller.set_time(int(time.time()))
            self.encoder_interface.set_time(int(time.time()))
        if state == 'ASSAY_FINISHED':
            self._assay_running = False
        else:
            self._check_for_unread_data_timer = Timer(self._CHECK_FOR_UNREAD_DATA_PERIOD,self._check_for_unread_data)
            self._check_for_unread_data_timer.start()


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':

    debug = False
    dev = MouseJoystickInterface(debug=debug)
