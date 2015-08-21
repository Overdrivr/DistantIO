# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# Send a single frame using serial protocol

from API.Protocol import Protocol
from API.SerialPort import SerialPort

class SerialMgr():
    def __init__(self):
        # Create protocol and give callback function
        self.protocol = Protocol(self.on_new_payload)
    
        # Create serial port manager
        self.serial = SerialPort(self.on_rx_data)
        self.serial.disconnect()
        self.serial.connect("COM8",115200)
        self.serial.start()

    def on_rx_data(self,c):
        print(c)
        self.protocol.decode(c)

    def on_new_payload(self,payload):
        print("decoded :",payload)
        

if __name__ == '__main__':
    
    mgr = SerialMgr()
    
    #data = input("Frame ?")
    data = "1"
    frame = mgr.protocol.encode(data.encode())
    #print("Sending "+str(frame))
    mgr.serial.write(frame)
        
    
    print("Done.")
