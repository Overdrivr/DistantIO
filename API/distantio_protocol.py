# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from DistantIO.API.crc import crc16
from struct import pack,unpack

class distantio_protocol():
    def __init__(self,on_tx_frame_callback):
        self.variables = []
        self.on_tx_frame_callback = on_tx_frame_callback
        self.payload_size = 14
        self.format_lookup = {0 : '>d',
                              1 : '>B',
                              2 : '>H',
                              3 : '>I',
                              4 : '>b',
                              5 : '>h',
                              6 : '>i'}

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
            raise IndexError("Frame size "+str(len(frame))+", expecting "+str(self.payload_size))

        # Second, check crc
        crc_frame = unpack('>H',frame[-2:])[0]
        crc_ref = crc16(frame[:-2])

        if crc_frame != crc_ref:
            raise ValueError("CRCs do not match, crc frame : "+str(crc_frame)+" versus reference :"+str(crc_ref))

        # Identify command
        cmd = frame[0]

        # returned-descriptor command
        if cmd == 0x00:
            returned_instruction['type'] = 'returned-descriptor'

            returned_instruction['var-id'] = unpack('>H',frame[1:3])[0]

            # Check format is valid
            raw_format = frame[3]
            if raw_format < 0 or raw_format > 6:
                raise ValueError("Received format identifier "+str(raw_format)+" unknown.")

            returned_instruction['var-type'] = self.format_lookup[frame[3]]

            returned_instruction['var-name'] = frame[4:12].decode(encoding='UTF-8')
            return returned_instruction

        # returned-value command
        if cmd == 0x01:
            returned_instruction['type'] = 'returned-value'

            returned_instruction['var-id'] = unpack('>H',frame[1:3])[0]

            # Check format is valid
            raw_format = frame[3]
            if raw_format < 0 or raw_format > 6:
                raise ValueError("Received format identifier "+str(frame)+" unknown.")

            fmt = self.format_lookup[frame[3]]
            returned_instruction['var-type'] = fmt

            returned_instruction['var-value'] = unpack(fmt,frame[4:12])[0]
            return returned_instruction

        # alive-signal command
        if cmd == 0x03:
            returned_instruction['type'] = 'alive-signal'
            return returned_instruction

        raise ValueError("Received command "+str(cmd)+" unknown.")
