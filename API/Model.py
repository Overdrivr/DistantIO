# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from API.SerialPort import SerialPort
from API.DistantIO import DistantIO
from API.Protocol import Protocol
from signalslot import Signal

class Model():
    def __init__(self):
        self.serial = SerialPort(self.on_rx_data_callback,self.on_connection_attempt_callback)
        self.protocol = Protocol(self.on_frame_decoded_callback)
        self.distantio = DistantIO(self.on_tx_frame_callback)

        # Signals
        self.signal_connected = Signal(args=['port'])
        self.signal_disconnected = Signal()
        self.signal_connecting = Signal()

    def connect(self,port,baudrate=115200):
        self.signal_connecting.emit()
        rtrn = self.serial.connect(port,baudrate)

    def disconnect(self):
        self.serial.disconnect()

    def finish(self):
        self.serial.disconnect()
        self.serial.stop()
        while(self.serial.isAlive()):
            print("Waiting for thread")

    def get_ports(self):
        return self.serial.get_ports()

    def write(self, variable_id, data):
        frame = self.distantio.write(variable_id,data)
        frame = self.protocol.encode(frame)
        self.serial.write(frame)

    ## Callbacks
        # RX : serial to protocol
    def on_rx_data_callback(self,char):
        self.protocol.decode(char)

        # RX : protocol to distantio
    def on_frame_decoded_callback(self,frame):
        self.distantio.process(frame)

        # TX : distantio to serial
    def on_tx_frame_callback(self,frame):
        frame = self.protocol.encode(frame)
        self.serial.write(frame)

    def on_connection_attempt_callback(self,message):
        if message in ["NO-PORT-FOUND","UNKNOWN-CONNECTION-ISSUE","CONNECTION-ISSUE","OTHER-PORTS-FOUND","DISCONNECTED"]:
           self.signal_disconnected.emit()
        else:
           self.signal_connected.emit(port=message)