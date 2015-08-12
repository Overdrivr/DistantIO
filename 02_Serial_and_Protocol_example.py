# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# Test of the protocol algorithm with dummy frames

from API.Protocol import Protocol
from API.SerialPort import SerialPort

def on_new_payload(payload):
    print("RX :",payload)

if __name__ == '__main__':
    # Create protocol and give callback function
    protocol = Protocol(on_new_payload)
    
    # Create serial port manager
    serialMgr = SerialPort()
    serialMgr.connect("COM8",115200)

    # ToDO implement serial port with callbacks

    while(serialMgr.running):
        pass
    print("Done.")
