# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# Test of the protocol algorithm with dummy frames

from API.Protocol import Protocol
from API.SerialPort import SerialPort

class SerialMgr():
    def __init__(self):
            
        # Create serial port manager
        self.serial = SerialPort(self.on_rx_data,self.on_connect_try_callback)
        self.serial.connect("COM7",9600)

    def on_rx_data(self,c):
        print(c.decode('ascii'),end='')

    def on_connect_try_callback(self,data):
        print(data)

if __name__ == '__main__':
    
    mgr = SerialMgr()
   

    while(mgr.serial.running):
        pass
    
    print("Done.")
