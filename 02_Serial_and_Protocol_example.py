# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# Test of the protocol algorithm with dummy frames

from API.Protocol import Protocol
from API.SerialPort import SerialPort

class SerialMgr():
    def __init__(self):
        # Create protocol and give callback function
        self.protocol = Protocol(self.on_new_payload)
    
        # Create serial port manager
        self.serial = SerialPort(self.on_rx_data)
        self.serial.connect("COM5",115200)
        self.serial.run()

    def on_rx_data(self,c):
        print(c)
        self.protocol.decode(c)

    def on_new_payload(self,payload):
        print("decoded :",payload)
        

if __name__ == '__main__':
    
    mgr = SerialMgr()

    while(mgr.serial.running):
        pass
    
    print("Done.")
