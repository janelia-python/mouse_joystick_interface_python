from __future__ import print_function, division
import time
import atexit
import os
import pathlib
from datetime import datetime
from threading import Timer
import csv
import json
import flatten_json

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
    dev.start_assay(set_path='~/set_example.csv')

    # optional mouse_joystick_controller methods
    dev.mouse_joystick_controller.set_properties_to_defaults(['ALL'])
    dev.mouse_joystick_controller.get_property_values(['ALL'])
    dev.mouse_joystick_controller.repeat_aborted_trial('setValue',False)
    dev.mouse_joystick_controller.get_assay_status()
    dev.mouse_joystick_controller.move_joystick_to_base_position()
    dev.mouse_joystick_controller.move_joystick_to_reach_position()
    duration = 10
    count = 1
    dev.mouse_joystick_controller.activate_lickport(duration,count)
    dev.mouse_joystick_controller.get_trial_timing_data()
    dev.mouse_joystick_controller.abort_trial()
    '''

    _CHECK_FOR_UNREAD_DATA_PERIOD = 4.0
    _SEPARATOR = '.'

    def __init__(self,*args,**kwargs):
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            kwargs.update({'debug': DEBUG})
            self.debug = DEBUG
        self._base_path = pathlib.Path('~/mouse_joystick').expanduser()
        self._args = args
        self._kwargs = kwargs
        t_start = time.time()
        atexit.register(self._exit_mouse_joystick_interface)
        self._assay_running = False
        self._trials_fieldnames = ['finished_trial_count',
                                   'successful_trial_count',
                                   'trial_aborted',
                                   'assay_aborted',
                                   'pull_threshold',
                                   'set_in_assay',
                                   'repeat_set_count',
                                   'block_in_set',
                                   'block_count',
                                   'trial_in_block',
                                   'block.repeat_trial_count',
                                   'block.pull_torque',
                                   'block.lickport_reward_duration',
                                   'block.reach_position.0',
                                   'block.reach_position.1',
                                   'trial_start',
                                   'mouse_ready',
                                   'joystick_ready',
                                   'pull',
                                   'push',
                                   'timeout',
                                   'trial_abort']
        self._block_fieldnames = ['repeat_trial_count',
                                  'pull_torque',
                                  'lickport_reward_duration',
                                  'reach_position.0',
                                  'reach_position.1']
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

    def start_assay(self,set_path):
        if self._assay_running:
            print('Assay already running.')
            return

        print('Starting assay...')

        print('Setting time.')
        self.mouse_joystick_controller.set_time(int(time.time()))

        print('Clearing any previous set from controller.')
        self.mouse_joystick_controller.clear_set()

        print('Importing new set csv file.')
        self._set_path = pathlib.Path(set_path).expanduser()
        if self._set_path.exists():
            print('Set csv file found. {0}'.format(self._set_path))
        else:
            print('Set csv file does not exist! {0}'.format(self._set_path))
            return

        print('Sending new set to controller.')
        with open(self._set_path) as set_csvfile:
            setreader = csv.DictReader(set_csvfile)
            checked_header = False
            for block_flat in setreader:
                if not checked_header:
                    if set(block_flat.keys()) == set(self._block_fieldnames):
                        print('Set csv file header is correct.')
                    else:
                        print('Set csv file header does not match this: {0}'.format(self._block_fieldnames))
                        return
                    checked_header = True
                block_unflattened = flatten_json.unflatten_list(block_flat,separator=self._SEPARATOR)
                block = {}
                for key, value in block_unflattened.items():
                    if isinstance(value,str):
                        block[key] = int(value)
                    elif isinstance(value,list):
                        block[key] = [int(element) for element in value]
                block_added = self.mouse_joystick_controller.add_block_to_set(block['repeat_trial_count'],
                                                                              block['pull_torque'],
                                                                              block['lickport_reward_duration'],
                                                                              block['reach_position'])
                if block_added == block:
                    print('Added block to set. {0}'.format(block_added))
                else:
                    raise RuntimeError('Block added does not equal block in csv file!')

        print('Setting up trial csv output file.')
        self._assay_path = self._base_path / self._get_date_time_str()
        self._assay_path.mkdir(parents=True,exist_ok=True)
        trials_filename = 'trials.csv'
        trials_path = self._assay_path / trials_filename
        self._trials_file = open(trials_path,'w')
        self._trials_writer = csv.DictWriter(self._trials_file,fieldnames=self._trials_fieldnames)
        self._trials_writer.writeheader()
        print('Trials.csv file created. {0}'.format(trials_path))

        self._assay_running = self.mouse_joystick_controller.start_assay()

        if self._assay_running:
            self._check_for_unread_data_timer = Timer(self._CHECK_FOR_UNREAD_DATA_PERIOD,self._check_for_unread_data)
            self._check_for_unread_data_timer.start()
            print('Assay running!')
        else:
            print('Assay not running!')
            self._cleanup()

    def abort_assay(self):
        self._assay_running = False
        self._cleanup()
        try:
            self.mouse_joystick_controller.abort_assay()
        except:
            pass

    def _cleanup(self):
        try:
            self._trials_file.close()
        except (AttributeError,ValueError):
            pass
        try:
            self._check_for_unread_data_timer.cancel()
        except AttributeError:
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
        state = status.pop('state')
        unread_trial_timing_data = status.pop('unread_trial_timing_data')
        if unread_trial_timing_data:
            trial_timing_data = self.mouse_joystick_controller.get_trial_timing_data()
            trial_timing_data_date_time = {key: self._get_date_time_str(value) for (key,value) in trial_timing_data.items()}
            trial_data = {**status,**trial_timing_data_date_time}
            trial_data = flatten_json.flatten(trial_data,separator=self._SEPARATOR)
            print('Trial data:')
            print(trial_data)
            self._trials_writer.writerow(trial_data)
            self.mouse_joystick_controller.set_time(int(time.time()))
        if state == 'ASSAY_FINISHED':
            self._assay_running = False
            self._cleanup()
        else:
            self._check_for_unread_data_timer = Timer(self._CHECK_FOR_UNREAD_DATA_PERIOD,self._check_for_unread_data)
            self._check_for_unread_data_timer.start()


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':

    debug = False
    dev = MouseJoystickInterface(debug=debug)
