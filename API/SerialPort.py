# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from threading import Thread
import serial
from queue import Queue
from serial.tools.list_ports import comports

#Serial data processing class
class SerialPort(Thread):
    def __init__(self,on_rx_data_callback,connection_attempt_callback):
        Thread.__init__(self)
        self.ser = serial.Serial()

        self.rx_data_callback = on_rx_data_callback
        self.connection_attempt_callback = connection_attempt_callback
        self.connection_attempt_callback("DISCONNECTED")

        # Starting thread
        self.running = True
        self.attempt_connect = False
        self.start()

    def connect(self,port,baudrate):
        self.ser.baudrate = baudrate
        self.ser.port = port

        portlist = self.get_ports()
        port_found = -1
        port_amount = 0
        terminate = False

        #List all COM ports
        for p, desc, hwid in sorted(portlist):
            port_amount+=1
            if p == self.ser.port:
                port_found = 1

        #In case no port is found
        if port_amount == 0:
            print('No COM port found.')
            self.connection_attempt_callback("NO-PORT-FOUND")

        #In case ports are found but not chosen one
        if port_amount > 0 and port_found == -1:
            print(port,' port not found but others are available.')
            self.connection_attempt_callback("OTHER-PORTS-FOUND")

        # If everything ok, start the connection in the thread
        self.attempt_connect = True


    def get_ports(self):
        return serial.tools.list_ports.comports()

    def write(self, frame):
        if self.ser.isOpen() and self.running:
                write_rtrn = self.ser.write(frame)

    def disconnect(self):
        self.ser.close()
        self.connection_attempt_callback("DISCONNECTED")

    def stop(self):
        self.running = False


    def run(self):
        #Main serial loop
        while self.running:
            if self.ser.isOpen():
                try:
                    inwaiting = self.ser.inWaiting()
                    if inwaiting > 0:
                        serialout = self.ser.read(inwaiting)
                        mv = memoryview(serialout).cast('c')
                        for c in mv:
                            self.rx_data_callback(c)
                except:
                    pass
            elif self.attempt_connect:
                self.attempt_connect = False
                try:
                    print("Connecting")
                    self.ser.open()
                    self.connection_attempt_callback("CONNECTED")
                except:
                    print("Serial port : Port ",self.ser.port," found but impossible to open. Try to physically disconnect.")
                    self.ser.close()
                    self.connection_attempt_callback("CONNECTION-ISSUE")

                if self.ser.isOpen():
                    print('Connected to port ',self.ser.port)
                    self.connection_attempt_callback(self.ser.port)
                else:
                    self.connection_attempt_callback("UNKNOWN-CONNECTION-ISSUE")

        print("Serial thread stopped.")
