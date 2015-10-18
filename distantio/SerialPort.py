# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from threading import Thread
import serial
from queue import Queue
from serial.tools.list_ports import comports
import logging
from .TimingUtils import timeit

#Serial data processing class
class SerialPort(Thread):
    def __init__(self,on_rx_data_callback):
        Thread.__init__(self)
        self.ser = serial.Serial()

        self.rx_data_callback = on_rx_data_callback

        self.threshold = 100
        self.connection_established = False

    def open(self,port,baudrate):
        self.ser.baudrate = baudrate
        self.ser.port = port
        # Start thread - this will try to establish connection
        self.start()

    def connected(self):
        return self.connection_established

    def get_ports(self):
        return serial.tools.list_ports.comports()

    def write(self, frame):
        if self.ser.isOpen() and self.running:
                write_rtrn = self.ser.write(frame)

    def close(self):
        self.running = False
        if self.isAlive():
            self.join()
        logging.info("SerialPort disconnected.")

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
        try:
            logging.info("Connecting to %s.",self.ser.port)
            self.ser.open()
        except:
            logging.error("port %s found but impossible to open. Try to physically disconnect.",self.ser.port)

        if self.ser.isOpen():
            logging.info("Connected to port %s successfully.",self.ser.port)
            self.running = True

        #Main serial loop
        while self.running:
            if self.ser.isOpen():
                self.serialRun()

        self.ser.close()
        self.connection_established = False
        logging.info('SerialPort thread stopped.')
