# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from API.Protocol import Protocol
from API.crc import *

class DistantIO():
    def __init__(self,on_tx_frame_callback):
        self.variables = []
        self.on_tx_frame_callback = on_tx_frame_callback

    # Returns the get-descriptors frame
    def get_descriptors_frame(self):
        packet = bytearray(14)
        # Build data frame
        packet[0] = 0x02
        packet[4] = 0xFF
        packet[11] = 0xFF
        # Compute CRC
        crc = crc16(packet[:-2]).to_bytes(2,byteorder='big')
        packet[12] = crc[0]
        packet[13] = crc[1]
        return packet

    def write_variable_frame(self, cmd_id,variable_id,data):
        packet = bytearray(14)
        print(packet)

    def process(self,frame):
        print("RX:"+str(frame))
