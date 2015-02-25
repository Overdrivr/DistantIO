# DistantIO
Convenient framework for reading and writing variables on a microcontroller in real time

## Authors
Rémi Bèges (python API + GUI)

Jerôme Mallet (GUI improvements)

Dan Faudemer (API improvements)

## Contents of this repository
### DistantIO
DistantIO is a complete framework for reading and writing variables on an MCU from a computer in real time.

It uses two software protocols on top of the serial port to construct data frames and exchange data with the MCU :

1. serial protocol (on top of serial port) : A simple frame delimiter protocol with byte stuffing
2. distantio protocol (on top of serial protocol) : A set of commands and defined frames for reading/writing variables 

Protocols are defined in serial_protocols_definition.xlsx

#### MCU side
Both protocols are implemented in MCU/DistantIO/

#### Computer side
A python API implementing both protocols to communicate with the MCU is provided. 
A GUI build with Tkinter is also supplied for communicating and debugging the MCU in a more friendly manner.
![gui main control screenshot](https://raw.githubusercontent.com/Overdrivr/Freescale_Cup/master/gui_main_control.png)
![gui plot screenshot](https://raw.githubusercontent.com/Overdrivr/Freescale_Cup/master/gui_plot.png)

## Supported Hardware
### "Freedom" board
"Freedom FRDM-KL25Z board" - Development platform for Freescale Kinetis L series MCU (Processor ARM Cortex M0+)
http://www.freescale.com/webapp/sps/site/prod_summary.jsp?code=FRDM-KL25Z

### Arduino
To be done.

## Requirements
### Serial port drivers
Usb serial port drivers (PEDrivers_install.exe) are available at :
http://www.pemicro.com/opensda/

### Python 
#### Core version
Python 3.4.2 minimum (https://www.python.org/downloads/)

#### Modules to install (manually or via pip)
* matplotlib 1.4.2 
* numpy 1.9.0 minimum
* scipy 0.14 minimum
* pyserial
* pyttk
* PyPubSub
