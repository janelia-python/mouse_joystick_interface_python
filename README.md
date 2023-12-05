- [About](#orge5ac949)
- [Example Usage](#orgab5654d)
- [Example Set CSV Input File](#org3f17bee)
- [Example Trials CSV Ouput File](#orge872842)
- [Installation](#orga22e627)
- [Development](#org3690cc6)

    <!-- This file is generated automatically from metadata -->
    <!-- File edits may be overwritten! -->


<a id="orge5ac949"></a>

# About

```markdown
- Python Package Name: mouse_joystick_interface
- Description: Python interface to the Dudman lab Mouse Joystick Rig.
- Version: 5.0.0
- Python Version: 3.10
- Release Date: 2023-12-05
- Creation Date: 2023-10-17
- License: BSD-3-Clause
- URL: https://github.com/janelia-pypi/mouse_joystick_interface_python
- Author: Peter Polidoro
- Email: peter@polidoro.io
- Copyright: 2023 Howard Hughes Medical Institute
- References:
  - https://github.com/janelia-kicad/mouse_joystick_controller
- Dependencies:
  - modular_client
  - flatten_json
```


<a id="orgab5654d"></a>

# Example Usage


## Python

```python
from mouse_joystick_interface import MouseJoystickInterface
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
```


## Command Line


<a id="org3f17bee"></a>

# Example Set CSV Input File

<p class="verse">
repeat\_trial\_count,pull\_torque,lickport\_reward\_duration,zero\_torque\_reward\_delay,reach\_position.0,reach\_position.1<br />
2,50,100,0,20,200<br />
3,75,120,0,30,300<br />
2,0,100,3,5,200<br />
</p>


<a id="orge872842"></a>

# Example Trials CSV Ouput File

<p class="verse">
finished\_trial\_count,successful\_trial\_count,trial\_aborted,assay\_aborted,pull\_threshold,set\_in\_assay,repeat\_set\_count,block\_in\_set,block\_count,trial\_in\_block,block.repeat\_trial\_count,block.pull\_torque,block.lickport\_reward\_duration,block.zero\_torque\_reward\_delay,block.reach\_position.0,block.reach\_position.1,trial\_start,mouse\_ready,joystick\_ready,pull,push,timeout,trial\_abort<br />
</p>


<a id="orga22e627"></a>

# Installation

<https://github.com/janelia-pypi/python_setup>


## GNU/Linux

1.  Drivers

    GNU/Linux computers usually have all of the necessary drivers already installed, but users need the appropriate permissions to open the device and communicate with it.
    
    Udev is the GNU/Linux subsystem that detects when things are plugged into your computer.
    
    Udev may be used to detect when a device is plugged into the computer and automatically give permission to open that device.
    
    If you plug a sensor into your computer and attempt to open it and get an error such as: "FATAL: cannot open /dev/ttyACM0: Permission denied", then you need to install udev rules to give permission to open that device.
    
    Udev rules may be downloaded as a file and placed in the appropriate directory using these instructions:
    
    [99-platformio-udev.rules](https://docs.platformio.org/en/stable/core/installation/udev-rules.html)

2.  Download rules into the correct directory

    ```sh
    curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core/master/scripts/99-platformio-udev.rules | sudo tee /etc/udev/rules.d/99-platformio-udev.rules
    ```

3.  Restart udev management tool

    ```sh
    sudo service udev restart
    ```

4.  Ubuntu/Debian users may need to add own “username” to the “dialout” group

    ```sh
    sudo usermod -a -G dialout $USER
    sudo usermod -a -G plugdev $USER
    ```

5.  After setting up rules and groups

    You will need to log out and log back in again (or reboot) for the user group changes to take effect.
    
    After this file is installed, physically unplug and reconnect your board.


## Python Code

The Python code in this library may be installed in any number of ways, chose one.

1.  pip

    ```sh
    python3 -m venv ~/venvs/mouse_joystick_interface
    source ~/venvs/mouse_joystick_interface/bin/activate
    pip install mouse_joystick_interface
    ```

2.  guix

    Setup guix-janelia channel:
    
    <https://github.com/guix-janelia/guix-janelia>
    
    ```sh
    guix install python-mouse-joystick-interface
    ```


## Windows


### Python Code

The Python code in this library may be installed in any number of ways, chose one.

1.  pip

    ```sh
    python3 -m venv C:\venvs\mouse_joystick_interface
    C:\venvs\mouse_joystick_interface\Scripts\activate
    pip install mouse_joystick_interface
    ```


<a id="org3690cc6"></a>

# Development


## Clone Repository

```sh
git clone git@github.com:janelia-pypi/mouse_joystick_interface_python.git
cd mouse_joystick_interface_python
```


## Guix


### Install Guix

[Install Guix](https://guix.gnu.org/manual/en/html_node/Binary-Installation.html)


### Edit metadata.org

```sh
make -f .metadata/Makefile metadata-edits
```


### Tangle metadata.org

```sh
make -f .metadata/Makefile metadata
```


### Develop Python package

```sh
make -f .metadata/Makefile guix-dev-container
exit
```


### Test Python package using ipython shell

```sh
make -f .metadata/Makefile guix-dev-container-ipython
import mouse_joystick_interface
exit
```


### Test Python package installation

```sh
make -f .metadata/Makefile guix-container
exit
```


### Upload Python package to pypi

```sh
make -f .metadata/Makefile upload
```


### Test direct device interaction using serial terminal

```sh
make -f .metadata/Makefile guix-dev-container-port-serial # PORT=/dev/ttyACM0
# make -f .metadata/Makefile PORT=/dev/ttyACM1 guix-dev-container-port-serial
? # help
[C-a][C-x] # to exit
```


## Docker


### Install Docker Engine

<https://docs.docker.com/engine/>


### Develop Python package

```sh
make -f .metadata/Makefile docker-dev-container
exit
```


### Test Python package using ipython shell

```sh
make -f .metadata/Makefile docker-dev-container-ipython
import mouse_joystick_interface
exit
```


### Test Python package installation

```sh
make -f .metadata/Makefile docker-container
exit
```
