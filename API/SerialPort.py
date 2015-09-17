# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from threading import Thread
import serial
from queue import Queue
from serial.tools.list_ports import comports
import logging
from functools import wraps
from time import time

def timed(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    start = time()
    result = f(*args, **kwds)
    elapsed = time() - start
    if elapsed > 0.016:
        print("took "+str(elapsed))
    return result
  return wrapper

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

        self.threshold = 100

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
            logging.error('no COM port found.')
            self.connection_attempt_callback("NO-PORT-FOUND")

        #In case ports are found but not chosen one
        if port_amount > 0 and port_found == -1:
            logging.error("%s port not found but others are available.",port)
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
        logging.info("SerialPort disconnected.")

    def stop(self):
        self.running = False

    @timed
    def serialRun(self):
        inwaiting = 0
        try:
            inwaiting = self.ser.inWaiting()
        except serial.SerialException as e:
            logging.warning("SerialPort caught %s",str(e))
        if inwaiting > 0:
            try:
                data = self.ser.read(inwaiting)
            except serial.SerialException as e:
                logging.warning("SerialPort caught %s",str(e))
            else:
                #for c in list(memoryview(data)):
                self.rx_data_callback(data)

        if inwaiting > self.threshold:
            self.threshold += 100
            logging.info("SerialPort overload."+str(inwaiting)+" characters in buffer. New threshold at "+str(self.threshold))
        if inwaiting < 100:
            self.threshold = 100


    def run(self):
        logging.info('SerialPort thread started.')
        #Main serial loop
        while self.running:
            if self.ser.isOpen():
                self.serialRun()

            elif self.attempt_connect:
                self.attempt_connect = False
                try:
                    logging.info("Connecting to %s.",self.ser.port)
                    self.ser.open()
                    self.connection_attempt_callback("CONNECTED")
                except:
                    logging.error("port %s found but impossible to open. Try to physically disconnect.",self.ser.port)
                    self.ser.close()
                    self.connection_attempt_callback("CONNECTION-ISSUE")

                if self.ser.isOpen():
                    logging.info("Connected to port %s successfully.",self.ser.port)
                    self.connection_attempt_callback(self.ser.port)
                else:
                    self.connection_attempt_callback("UNKNOWN-CONNECTION-ISSUE")

        logging.info('SerialPort thread stopped.')
