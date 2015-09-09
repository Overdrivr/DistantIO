# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from DistantIO.API.crc import crc16
from struct import pack,unpack

class distantio_protocol():
    def __init__(self):
        self.variables = []
        self.payload_size = 14
        self.format_lookup = {0 : '>xxxxf',
                              1 : '>xxxxxxxB',
                              2 : '>xxxxxxH',
                              3 : '>xxxxI',
                              4 : '>xxxxxxxb',
                              5 : '>xxxxxxh',
                              6 : '>xxxxi'}

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

    # Returns the write-value frame
    def get_write_variable_frame(self,variable_id,variable_type,value):
        packet = bytearray(14)

        packet[0] = 0x04
        packet[1:3] = variable_id.to_bytes(2,byteorder='big')
        packet[3] = variable_type
        packet[4:12] = pack(self.format_lookup[variable_type],value)
        packet[12:] = crc16(packet[:-2]).to_bytes(2,byteorder='big')

        return packet

    # Returns the start-reading frame
    def get_start_readings_frame(self,variable_id,variable_type):
        packet = bytearray(14)

        packet[0] = 0x05
        packet[1:3] = variable_id.to_bytes(2,byteorder='big')
        packet[3] = variable_type
        packet[4] = 0xEE
        packet[11] = 0xEE
        packet[12:] = crc16(packet[:-2]).to_bytes(2,byteorder='big')

        return packet

    # Returns the stop-reading frame
    def get_stop_readings_frame(self,variable_id,variable_type):
        packet = bytearray(14)

        packet[0] = 0x06
        packet[1:3] = variable_id.to_bytes(2,byteorder='big')
        packet[3] = variable_type
        packet[4] = 0xDD
        packet[11] = 0xDD
        packet[12:] = crc16(packet[:-2]).to_bytes(2,byteorder='big')

        return packet

    # Returns the stop-all frame
    def get_stop_read_all_values_frame(self,variable_id):
        packet = bytearray(14)

        packet[0] = 0x07
        packet[4] = 0xCC
        packet[11] = 0xCC
        packet[12:] = crc16(packet[:-2]).to_bytes(2,byteorder='big')

        return packet

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
            raise ValueError("CRCs do not match, crc frame : "+str(crc_frame)+" versus reference :"+str(crc_ref)+". Full frame:"+str(frame))

        # Identify command
        cmd = frame[0]

        # returned-descriptor command
        if cmd == 0x00:
            returned_instruction['type'] = 'returned-descriptor'
            returned_instruction['var-id'] = unpack('>H',frame[1:3])[0]

            # Check format is valid
            raw_format = frame[3] & 0x0F
            if raw_format < 0 or raw_format > 6:
                raise ValueError("Received format identifier "+str(raw_format)+" unknown.")

            returned_instruction['var-type'] = raw_format
            returned_instruction['var-writeable'] = ((frame[3])>>4 & 0x0F == 0x0F)
            returned_instruction['var-name'] = frame[4:12].decode(encoding='UTF-8')
            return returned_instruction

        # returned-value command
        if cmd == 0x01:
            returned_instruction['type'] = 'returned-value'
            returned_instruction['var-id'] = unpack('>H',frame[1:3])[0]

            # Check format is valid
            raw_format = frame[3] & 0x0F
            if raw_format < 0 or raw_format > 6:
                raise ValueError("Received format identifier "+str(frame)+" unknown.")

            returned_instruction['var-type'] = raw_format
            returned_instruction['var-value'] = unpack(self.format_lookup[raw_format],frame[4:12])[0]
            return returned_instruction

        # alive-signal command
        if cmd == 0x03:
            returned_instruction['type'] = 'alive-signal'
            return returned_instruction

        raise ValueError("Received command "+str(cmd)+" unknown.")
