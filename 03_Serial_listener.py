# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# Test of the protocol algorithm with dummy frames

from API.Protocol import Protocol
from API.SerialPort import SerialPort

class SerialMgr():
    def __init__(self):
            
        # Create serial port manager
        self.serial = SerialPort(self.on_rx_data)
        self.serial.connect("COM5",9600)
        self.serial.start()

    def on_rx_data(self,c):
        print(c)        

if __name__ == '__main__':
    
    mgr = SerialMgr()
   

    while(mgr.serial.running):
        pass
    
    print("Done.")
