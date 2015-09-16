# DistantIO
Convenient framework for reading and writing variables on a microcontroller in real time. This is a master-slave protocol.
Master can be for instance a computer and the slave and embedded device such as a MicroController Unit (MCU).

The whole program was designed to be simple to use.

On the slave side, only three steps are required.
Simply register variables during initialization time, feed the incoming characters to the API, update it regularly and you're good to go.

Master side, the user interface provided can be used as is, for reading/writing/plotting MCU variables.
Or you can ditch it entirely and develop your own user interface with the API. ;)

## Authors
Rémi Bèges (python API + GUI)
Jerôme Mallet (GUI improvements)
Dan Faudemer (API improvements)

## Contents of this repository
### Master-side User Interface
The User Interface is made with Tkinter/ttk.
It is supplied for communicating with the MCU in a more friendly manner.
The UI is light but gives a good example on how to use the API.

### Master-side API
The master-side API is entirely located in the API/ folder. The Model class exposes all the methods you will need to call in your application.
To avoid coupling from API to UI, the Model class also defines a set of signals, which you can connect to slots. It is using the lightweight python module signalslot (<https://pypi.python.org/pypi/signalslot/0.1.0>).

To use the API in your project, simply copy API/ folder into your project folder. This project is not hosted on PyPi and cannot be installed using pip.

### Slave-side
#### C implementation
A first implementation in C (standard C99) is available in Slave/C/
Simply add the 6 files to your project.

See the examples (todo) or wiki (todo) for detailed instructions.

Supported Boards:
* Freescale Freedom boards (KL25Z, KL46Z, etc).
* Arduino : The implementation is standard C, so you should be able to simply add it to any Arduino program. Haven't tested it though
* And any other board programmed in C language.

#### ARM mbed
The C implementation is also in the process of being released as a library on the ARM mbed platform (<https://developer.mbed.org/>).
This would mean the library will be supported by any MCU running on an ARM processor.

## Protocols
Two different protocols are used in distantio.
Frames are delimited using flags with a classic byte stuffing algorithm.
Frames are fixed-size, because this reduces at lot the constraints on the slave code.

The second protocol is the core of distantio and defines what is contained in a delimited frame.
Each frames carries a 16 bits CRC (Cyclic Redundancy Check) to ensure the received value was not corrupted during transport or processing.

Protocols are defined in serial_protocols_definition.xlsx

## Python installation requirements
### Core version
Python 3.4.2 minimum (https://www.python.org/downloads/)

If you have an older python version and wish to keep both, have a look at the virtualenv module (<https://pypi.python.org/pypi/virtualenv>).
This module will enable you to switch between python versions/installations with a simple command

### Modules to install (manually or via pip)
* matplotlib 1.4.2
* numpy 1.9.0 minimum
* scipy 0.14 minimum
* pyserial
* pyttk
* pytest (optional, for running tests)
* pytest-cov (optional, for getting test coverage)
* tkinter (optionnal, for running the UI)
* ttk (optionnal, for running the UI)


The UI can be launched by running in a console pointing to DistantIO/

```bash
python application.py
```

You will most likely have import errors from the API. If this is the case, add the DistantIO **root** folder to the PYTHONPATH.
If your folder is for instance in C:/Documents/GitHub/DistantIO, add C:/Documents/Github to PYTHONPATH.
*Note : If you have spaces in your pathname, don't forget to use "".*
For instance with C:/Program Files/GitHub/DistantIO add C:/"Program Files"/Github to PYTHONPATH

### IMPORTANT
Additional Setup steps
In order for python import system to work properly, add the PARENT folder of DistantIO to the PYTHONPATH system variable.


## Running tests
Some parts of the API can be automatically tests using pytest and pytest-cov.
You can run the following commands in a console pointing to DistantIO/ to run the tests
'''
py.test --cov --cov-report html -v
'''
This will have a verbose (-v) output and generate a coverage report in html format that you can find in the generated htmlcov/ folder.
Open index.html in a browser to see the results.

## Furure work for slave-side
* C++ implementation
* implementation on the very promising ARM yotta (<http://www.mbed.com/en/development/software/tools/yotta/>)
