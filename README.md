# DistantIO
Convenient framework for reading and writing variables on a microcontroller in real time

## Authors
Rémi Bèges (python API + GUI)

Jerôme Mallet (GUI improvements)

Dan Faudemer (API improvements)

## Contents of this repository
### Python API
DistantIO is a simple framework for reading and writing variables on an MCU from a computer in real time.

It uses two software protocols on top of the serial port to construct data frames and exchange data with the MCU :

1. serial protocol (on top of serial port) : A simple frame delimiter protocol with byte stuffing
2. distantio protocol (on top of serial protocol) : A set of commands and defined frames for reading/writing variables

Protocols are defined in serial_protocols_definition.xlsx

### MCU API
Both protocols are implemented in MCU/DistantIO/
Note : In process
Supported :
* Almost completely Freescale Freedom boards (KL25Z, KL46Z, etc).
* Arduino : Planned

### Bonus - User Interface
A User Interface made with Tkinter/ttk is also supplied for communicating with the MCU in a more friendly manner. API is completely decoupled from it.
The UI is a rather big example in itself of using the API.
The UI can be launched by running application.py in the root folder

## Python installation requirements
### Core version
Python 3.4.2 minimum (https://www.python.org/downloads/)

### Modules to install (manually or via pip)
* matplotlib 1.4.2
* numpy 1.9.0 minimum
* scipy 0.14 minimum
* pyserial
* pyttk
* pytest (optional, for running tests)
* pytest-cov (optional, for getting test coverage)

### Additional Setup steps
In order for python import system to work properly, add the PARENT folder of DistantIO to the PYTHONPATH system variable.
If your folder is for instance in C:/Documents/GitHub/DistantIO, add C:/Documents/Github to PYTHONPATH

## Running tests
Some parts of the API can be automatically tests using pytest and pytest-cov.
You can run the following commands in a console pointing to DistantIO/ to run the tests
'''
py.test --cov --cov-report html -v
'''
This will have a verbose (-v) output and generate a coverage report in html format that you can find in the generated htmlcov/ folder.
Open index.html in a browser to see the results.
