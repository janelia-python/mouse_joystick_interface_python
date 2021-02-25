import pathlib
import codecs
import setuptools


here = pathlib.Path(__file__).resolve().parent

with codecs.open(here.joinpath('DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='mouse_joystick_interface',

    use_scm_version = True,
    setup_requires=['setuptools_scm'],

    description='Mouse joystick interface for communicating with mouse joystick controller.',
    long_description=long_description,

    url='https://github.com/janelia-pypi/mouse_joystick_interface_python',

    author='Peter Polidoro',
    author_email='peterpolidoro@gmail.com',

    license='BSD',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
    ],

    keywords='modular serial arduino device client modulardevice modular-device modular_device modularclient modular-client mouse_joystick_interface json json-rpc',

    packages=setuptools.find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['modular_client',
    ],
)
