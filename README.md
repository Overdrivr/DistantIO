# DistantIO
DistantIO is a convenient framework for reading and writing variables on a microcontroller in real time. This is a master-slave protocol.
Master can be for instance a computer and the slave an embedded device such as a MicroController Unit (MCU).

The whole program was designed to be simple to setup and use.

On the slave side, only two steps are required.
Simply register variables during initialization time and update the API from time to time and you're good to go.

Master side, the user interface provided can be used as is, for reading/writing/plotting MCU variables.
Or you can ditch it entirely and develop your own user interface with the API. ;)

## Authors
* Rémi Bèges
* Jerôme Mallet (UI improvements)
* Dan Faudemer (python API improvements)

## Contents of this repository
TODO : rewrite, speak about features.

### Master-side User Interface
The User Interface is made with Tkinter/ttk.
It is supplied for communicating with the MCU in a more friendly manner.
The UI is light but gives a good example on how to use the API.

### Master-side API
The master-side API is entirely located in the API/ folder. The Model class exposes all the methods you will need to call in your application.
To avoid coupling from API to UI, the Model class also defines a set of signals, which you can connect to slots in your UI. It is using the lightweight python module signalslot (<https://pypi.python.org/pypi/signalslot/0.1.0>).

To use distantio in your project, simply copy distantio folder into your project folder, and add your project folder to the PYTHONPATH.

This project is *not* hosted on PyPi yet and cannot be installed using pip. This might change in a near future now that both master and slave APIs are going closer to be stable.

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
The C implementation is available on ARM mbed development platform(<https://developer.mbed.org/users/Overdrivr/code/DistantIO/>).
This increases considerably the amount of supported hardware platform. See the full list on <https://developer.mbed.org/platforms/>

A C++ interface is in development.

## Python installation requirements
### Core version
Python 3.4.2 minimum (https://www.python.org/downloads/)

If you have an older python version and wish to keep both, have a look at the virtualenv module (<https://pypi.python.org/pypi/virtualenv>).
This module will enable you to switch between python versions/installations with a simple console command.

### Modules to install (manually or via pip)
TODO : Use virtualenv requirements system for installing modules. But install numpy first from precompiled sources
* pyserial
* tkinter (optionnal, for running the UI)
* pyttk (optionnal, for running the UI)
* matplotlib 1.4.2 (optionnal, for running the UI)
* numpy 1.9.0 minimum (optionnal, for running the UI)
* scipy 0.14 minimum (optionnal, for running the UI)
* pytest (optional, for running tests)
* pytest-cov (optional, for getting test coverage)


## Running the User Interface
The UI can be launched by running the following command in a console pointing to DistantIO folder

```bash
python application.py
```

You will most likely have import errors from the API. If this is the case, add the DistantIO folder to the PYTHONPATH.

*Note : If you have spaces in your pathname, don't forget to use "".*

For instance C:/Program Files/GitHub/DistantIO -> C:/"Program Files"/Github/DistantIO

## Running tests
For now, both protocols in the API can be automatically tested using pytest.
You can run the following commands in a console pointing to DistantIO/ to run the tests
```bash
py.test -v
```

This will have a verbose (-v) output. It will tell you which individual test passed or failed.

Coverage results can additionally be obtained using pytest-cov using the --cov flag

```bash
py.test --cov --cov-report html -v
```

It will also generate a coverage report in html format that you can find in the generated htmlcov/ folder.
Open index.html in a browser to see the coverage results.

## Protocols
Two different protocols are used in distantio.
Serial frames are delimited using flags with a classic byte-stuffing algorithm.
Frames are fixed-size, because this reduces at lot the constraints on the slave code.

The second protocol is the core of distantio and defines what is contained in a delimited frame.
Each frames carries a 16 bits CRC (Cyclic Redundancy Check) to ensure the received value was not corrupted during transport or processing.

Protocols are defined in serial_protocols_definition.xlsx

## Furure work for slave-side
* C++ implementation
* implementation on the very promising ARM yotta (<http://www.mbed.com/en/development/software/tools/yotta/>)
