import multiprocessing
from .Protocol import Protocol

class Worker(multiprocessing.Process):
    def __init__(self,input_queue,output_queue,new_data_condition,stop_condition):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.wait_condition = new_data_condition
        self.stop_condition = stop_condition
        self.protocol = Protocol(self.on_frame_decoded_callback)

    def run(self):
        print("started")
        while not self.stop_condition.is_set():
            # Wait for new data to be put in the queue
            self.wait_condition.wait()
            while not self.input_queue.empty():
                data = self.input_queue.get()
                for c in list(memoryview(data)):
                    self.protocol.decode(c)
            self.wait_condition.clear()

        print("stopped")

    def on_frame_decoded_callback(self,frame):
        self.output_queue.put(frame)
