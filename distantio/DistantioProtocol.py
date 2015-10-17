# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from distantio.crc import crc16
from struct import pack,unpack
import logging

class distantio_protocol():
    def __init__(self):
        self.variables = []

        self.format_lookup = {0 : '>xxxxf',
                              1 : '>xxxxxxxB',
                              2 : '>xxxxxxH',
                              3 : '>xxxxI',
                              4 : '>xxxxxxxb',
                              5 : '>xxxxxxh',
                              6 : '>xxxxi'}

        # Frame description
        self.frame_size = 20

        self.cmd_start = 0

        self.data_id_start = 1
        self.data_id_end = 2 + 1 # +1 for slicing

        self.data_type_start = 3

        self.extraid_1_start = 4
        self.extraid_1_end = 7 + 1

        self.extraid_2_start = 8
        self.extraid_2_end = 9 + 1

        self.data_start = 10
        self.data_end = 17 + 1

        self.var_name_start = 4
        self.var_name_end = 17 + 1

        self.crc_start = 18
        self.crc_end = 19 + 1


    # Returns the get-descriptors frame
    def get_descriptors_frame(self):
        packet = bytearray(self.frame_size)
        # Build data frame
        packet[self.cmd_start] = 0x02
        # Compute and pack CRC
        packet[self.crc_start:self.crc_end] = crc16(packet[:-2]).to_bytes(2,byteorder='big')
        return packet

    # Returns the write-value frame
    def get_write_value_frame(self,variable_id,variable_type,value):
        packet = bytearray(self.frame_size)
        # Cast value to chosen type
        if variable_type == 0:
            value = float(value)
        else:
            value = int(value)

        packet[self.cmd_start] = 0x04
        packet[self.data_id_start:self.data_id_end] = variable_id.to_bytes(2,byteorder='big')
        packet[self.data_type_start] = variable_type
        packet[self.data_start:self.data_end] = pack(self.format_lookup[variable_type],value)
        packet[self.crc_start:self.crc_end] = crc16(packet[:-2]).to_bytes(2,byteorder='big')

        return packet

    # Returns the start-reading frame
    def get_start_reading_frame(self,variable_id,variable_type):
        packet = bytearray(self.frame_size)

        packet[self.cmd_start] = 0x05
        packet[self.data_id_start:self.data_id_end] = variable_id.to_bytes(2,byteorder='big')
        packet[self.data_type_start] = variable_type
        packet[self.crc_start:self.crc_end] = crc16(packet[:-2]).to_bytes(2,byteorder='big')

        return packet

    # Returns the stop-reading frame
    def get_stop_reading_frame(self,variable_id,variable_type):
        packet = bytearray(self.frame_size)

        packet[self.cmd_start] = 0x06
        packet[self.data_id_start:self.data_id_end] = variable_id.to_bytes(2,byteorder='big')
        packet[self.data_type_start] = variable_type
        packet[self.crc_start:self.crc_end] = crc16(packet[:-2]).to_bytes(2,byteorder='big')

        return packet

    def process(self,frame):
        returned_instruction = dict()
        returned_instruction['type'] = None

        # First, check data size
        if len(frame) != self.frame_size:
            raise IndexError("Frame size "+str(len(frame))+", expecting "+str(self.frame_size))

        # Second, check crc
        crc_frame = unpack('>H',frame[-2:])[0]
        crc_ref = crc16(frame[:-2])

        if crc_frame != crc_ref:
            raise ValueError("CRCs do not match, crc frame : "+str(crc_frame)+" versus reference :"+str(crc_ref))

        # Identify command
        cmd = frame[self.cmd_start]

        # returned-descriptor command
        if cmd == 0x00:
            # Check format is valid
            raw_format = frame[self.data_type_start] & 0x0F
            if raw_format < 0 or raw_format > 7:
                raise ValueError("Received format identifier "+str(raw_format)+" unknown.")

            # Received a group descriptor
            if raw_format == 7:
                returned_instruction['type'] = 'returned-group-descriptor'
                value = unpack('>H',(frame[self.data_id_start:self.data_id_end]))[0]
                value = (value >> 10) & 0x3F
                returned_instruction['group-id'] = value
                returned_instruction['group-name'] = frame[self.var_name_start:self.var_name_end].decode(encoding='UTF-8')
            else:
                returned_instruction['type'] = 'returned-descriptor'
                var_id = unpack('>H',(frame[self.data_id_start:self.data_id_end]))[0]
                var_id = var_id & 0x3FF
                var_group = unpack('>H',(frame[self.data_id_start:self.data_id_end]))[0]
                var_group = (var_group >> 10) & 0x3F
                returned_instruction['var-id'] = var_id
                returned_instruction['var-type'] = raw_format
                returned_instruction['var-writeable'] = ((frame[self.data_type_start])>>4 & 0x0F == 0x0F)
                returned_instruction['var-name'] = frame[self.var_name_start:self.var_name_end].decode(encoding='UTF-8')
                returned_instruction['var-group'] = var_group
            return returned_instruction

        # returned-value command
        if cmd == 0x01:
            returned_instruction['type'] = 'returned-value'

            # Check format is valid
            raw_format = frame[self.data_type_start] & 0x0F
            if raw_format < 0 or raw_format > 6:# TODO : Change with format lookup
                raise ValueError("Received format identifier "+str(frame)+" unknown.")

            value = unpack('>H',(frame[self.data_id_start:self.data_id_end]))[0]
            value = value & 0x3FF
            returned_instruction['var-id'] = value
            returned_instruction['var-type'] = raw_format
            returned_instruction['var-value'] = unpack(self.format_lookup[raw_format],frame[self.data_start:self.data_end])[0]
            returned_instruction['var-time'] = unpack('>f',frame[self.extraid_1_start:self.extraid_1_end])[0]
            returned_instruction['var-array-index'] = unpack('>H',frame[self.extraid_2_start:self.extraid_2_end])[0]
            return returned_instruction

        # alive-signal command
        if cmd == 0x03:
            returned_instruction['type'] = 'alive-signal'
            return returned_instruction

        # Emergency send
        if cmd == 0x09:
            returned_instruction['type'] = 'emergency-send'
            returned_instruction['data-id'] = frame[self.data_id_start:self.data_id_end].decode(encoding='UTF-8')
            # Check format is valid
            raw_format = frame[self.data_type_start] & 0x0F
            if raw_format < 0 or raw_format > 6:# TODO : Change with format lookup
                raise ValueError("Received format identifier "+str(frame)+" unknown.")

            returned_instruction['data-type'] = raw_format
            returned_instruction['data-time'] = unpack('>f',frame[self.extraid_1_start:self.extraid_1_end])[0]
            returned_instruction['data-index'] = unpack('>H',frame[self.extraid_2_start:self.extraid_2_end])[0]
            returned_instruction['data-value'] = unpack(self.format_lookup[raw_format],frame[self.data_start:self.data_end])[0]
            return returned_instruction

        raise ValueError("Received command "+str(cmd)+" unknown.")
