# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from API.Protocol import Protocol

class DistantIO():
    def __init__(self,on_tx_frame_callback):
        self.variables = []
        self.on_tx_frame_callback = on_tx_frame_callback
        
    def write(self, variable_id, data):        
        pass

    def process(self,frame):
        pass
