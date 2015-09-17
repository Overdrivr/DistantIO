# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from .SerialPort import SerialPort
from .distantio_protocol import distantio_protocol
from .Protocol import Protocol
from .Worker import Worker
from signalslot import Signal
import threading
import logging
from logging.handlers import RotatingFileHandler
import binascii
import multiprocessing as mp
import time

class Model():
    def __init__(self):
        # Init logging facility
        # From : http://sametmax.com/ecrire-des-logs-en-python/
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        file_handler = RotatingFileHandler('api_log.log', 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)

        # Signals
        self.signal_connected = Signal(args=['port'])
        self.signal_disconnected = Signal()
        self.signal_connecting = Signal()
        self.signal_MCU_state_changed = Signal(args=['alive'])
        self.signal_received_descriptor = Signal(args=['var_id','var_type','var_name','var_writeable','group_id'])
        self.signal_received_group_descriptor = Signal(args=['group_id','group_name'])
        self.signal_received_value = Signal(args=['var_id','var_type','var_value'])

        self.serial = SerialPort(self.on_rx_data_callback,self.on_connection_attempt_callback)
        self.distantio = distantio_protocol()
        self.protocol = Protocol(self.unused)

        # Queue holding received characters to be processed by worker process
        self.input_queue = mp.Queue()
        # Queue holding decoded frames
        self.output_queue = mp.Queue()
        # Conditions for controlling run process
        self.condition_new_rx_data = mp.Event()
        self.condition_new_rx_data.clear()
        self.condition_run_process = mp.Event()
        self.condition_run_process.clear()
        # Worker process for decoding characters
        self.worker = Worker(self.input_queue,self.output_queue,self.condition_new_rx_data,self.condition_run_process)
        self.worker.start()

        # Threaded function for decoding received frames
        self.condition_stop_thread = threading.Event()
        self.frame_decoding_thread = threading.Thread(target=self.process_output_queue)
        self.frame_decoding_thread.start()

        # Timer for monitoring MCU alive
        self.mcu_died_delay = 2.0
        self.mcu_alive_timer = threading.Timer(self.mcu_died_delay,self.on_mcu_lost_connection)

        self.variable_list = dict()
        self.connected = False

        logging.info('DistantIO API initialized successfully.')

    def connect(self,port,baudrate=115200):
        if not self.connected:
            self.signal_connecting.emit()
            self.serial.connect(port,baudrate)
            self.mcu_alive_timer = threading.Timer(self.mcu_died_delay,self.on_mcu_lost_connection)
            self.mcu_alive_timer.start()

    def disconnect(self):
        self.serial.disconnect()
        self.signal_MCU_state_changed.emit(alive=False)
        self.mcu_alive_timer.cancel()
        if self.mcu_alive_timer.isAlive():
            self.mcu_alive_timer.join()
        self.connected = False

    def finish(self):
        self.disconnect()
        self.serial.stop()
        self.serial.join()
        logging.info('Serial thread joined.')
        print("Notifying")
        self.condition_new_rx_data.set()
        self.condition_run_process.set()
        print("Notified")
        self.worker.join()
        print("Joined. Notifying thread")
        self.condition_stop_thread.set()
        print("Notified thread.")
        self.frame_decoding_thread.join()
        logging.info('API terminated successfully.')

    def get_ports(self):
        return self.serial.get_ports()

    ### Distant IO calls to MCU
    # Ask the MCU to return all descriptors
    def request_descriptors(self):
        logging.info('requested all descriptors to MCU.')
        frame = self.distantio.get_descriptors_frame()
        frame = self.protocol.encode(frame)
        self.serial.write(frame)

    # Ask the MCU to write a variable
    def request_write(self, variable_id, data):
        if not variable_id in self.variable_list:
            logging.error("variable id provided "+str(variable_id)+" not found.")
            return
        # Check data is number
        try:
            # Cast to float and see if that fails
            dummy = float(data)
        except ValueError:
            logging.error("value provided "+str(data)+" not correct.")
            return

        logging.info('requested MCU to write '+str(data)+' to var id '+str(variable_id)+'.')
        frame = self.distantio.get_write_variable_frame(variable_id,self.variable_list[variable_id]['type'],data)
        frame = self.protocol.encode(frame)
        self.serial.write(frame)

    # Ask the MCU to read all variables
    def request_read_all(self):
        for key in self.variable_list:
            logging.info('requested to receive readings of var id '+str(key)+'.')
            frame = self.distantio.get_start_readings_frame(key,self.variable_list[key]['type'])
            frame = self.protocol.encode(frame)
            self.serial.write(frame)

    def process_output_queue(self):
        while not self.condition_stop_thread.is_set():
            if not self.output_queue.empty():
                frame = self.output_queue.get()
                self.decode_frame(frame)
    ## Callbacks
        # RX : serial to protocol
    def on_rx_data_callback(self,data):
        #self.protocol.decode(c)
        self.input_queue.put(data)
        self.condition_new_rx_data.set()

        # RX : protocol to distantio
    def decode_frame(self,frame):
        try:
            instruction = self.distantio.process(frame)
        except IndexError as e:
            logging.warning("received error "+str(e)+" with frame : %s",binascii.hexlify(frame))
            return
        except ValueError as e:
            logging.warning("received error "+str(e)+" with frame : %s",binascii.hexlify(frame))
            return

        # If distantio received a alive signal
        if instruction['type'] == "alive-signal":
            # Restart the timer
            self.mcu_alive_timer.cancel()
            self.mcu_alive_timer.join()

            self.mcu_alive_timer = threading.Timer(self.mcu_died_delay,self.on_mcu_lost_connection)

            self.mcu_alive_timer.start()
            self.signal_MCU_state_changed.emit(alive=True)

        # if returned-value
        elif instruction['type'] == 'returned-value':
            self.signal_received_value.emit(var_id=instruction['var-id'],
                                            var_type=instruction['var-type'],
                                            var_value=instruction['var-value'])
        # if returned-descriptor
        elif instruction['type'] == 'returned-descriptor':
            if not instruction['var-id'] in self.variable_list:
                self.variable_list[instruction['var-id']] = dict()
                self.variable_list[instruction['var-id']]['type'] = instruction['var-type']
                self.variable_list[instruction['var-id']]['name'] = ['var-name']
                self.variable_list[instruction['var-id']]['writeable'] = ['var-writeable']

            self.signal_received_descriptor.emit(var_id=instruction['var-id'],
                                                 var_type=instruction['var-type'],
                                                 var_name=instruction['var-name'],
                                                 var_writeable=instruction['var-writeable'],
                                                 group_id=instruction['var-group'])
        elif instruction['type'] == 'returned-group-descriptor':
            self.signal_received_group_descriptor.emit(group_id=instruction['group-id'],
                                                       group_name=instruction['group-name'])
        else:
            logging.error("Unknown instruction :"+str(instruction))


    def on_mcu_lost_connection(self):
        self.signal_MCU_state_changed.emit(alive=False)

        # TX : distantio to serial
    def on_tx_frame_callback(self,frame):
        frame = self.protocol.encode(frame)
        self.serial.write(frame)

    def on_connection_attempt_callback(self,message):
        if message in ["NO-PORT-FOUND","UNKNOWN-CONNECTION-ISSUE","CONNECTION-ISSUE","OTHER-PORTS-FOUND","DISCONNECTED"]:
           self.signal_disconnected.emit()
        else:
           self.signal_connected.emit(port=message)

    def unused(self,frame):
        logging.error("Local protocol decoded frame "+str(frame)+" instead of Worker")
