import multiprocessing
from .FrameProtocol import Protocol
from .DistantioProtocol import distantio_protocol
import logging
import binascii

class Worker(multiprocessing.Process):
    def __init__(self,input_queue,output_queue,new_data_condition,stop_condition):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.wait_condition = new_data_condition
        self.stop_condition = stop_condition
        self.protocol = Protocol(self.on_frame_decoded_callback)
        self.decoder = distantio_protocol()

    def run(self):
        print("started")
        while not self.stop_condition.is_set():
            # Wait for new data to be put in the queue
            if not self.input_queue.empty() :
                data = self.input_queue.get()
                for c in list(memoryview(data)):
                    self.protocol.decode(c)

        print("stopped")

    def on_frame_decoded_callback(self,frame):
        try:
            instruction = self.decoder.process(frame)
        except IndexError as e:
            logging.warning("received error "+str(e)+" with frame : %s",binascii.hexlify(frame))
            return
        except ValueError as e:
            logging.warning("received error "+str(e)+" with frame : %s",binascii.hexlify(frame))
            return
        else:
            self.output_queue.put(instruction)
