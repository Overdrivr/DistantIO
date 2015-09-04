# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from API.Protocol import Protocol
from API.crc import *
from struct import *

class DistantIO():
    def __init__(self,on_tx_frame_callback):
        self.variables = []
        self.on_tx_frame_callback = on_tx_frame_callback
        self.payload_size = 14

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
        returned_instruction = dict()
        returned_instruction['type'] = None

        # First, check data size
        if len(frame) != self.payload_size:
            return returned_instruction

        # Second, check crc
        crc_frame = unpack('H',frame[-2:])[0]
        crc_ref = crc16(frame[:-2])

        if crc_frame != crc_ref:
            print("CRC don't match - aborting.")
            print("Frame : "+str(frame))
            print("Local crc : "+str(crc_ref))
            print("Frame crc : "+str(crc_frame))
            return returned_instruction

        # Identify command
        cmd = frame[0]

        # Alive signal
        if cmd == 0x03:
            returned_instruction['type'] = 'alive-signal'
            return returned_instruction
