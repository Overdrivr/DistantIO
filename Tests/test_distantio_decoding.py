# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# See __init__.py file on how to run tests automatically

from DistantIO.API.DistantioProtocol import distantio_protocol
from DistantIO.API.crc import crc16
from struct import pack,unpack
import pytest
# test decoding unkown command

# test decoding valid returned-descriptor frame
def test_returned_descriptor_variable_non_writeable():
    distantio = distantio_protocol()

    # inputs
    var_id = 999
    group_id = 18
    name = "testvariable 1"
    fmt = 3

    # formatting
    formatted_name = "{:14s}".format(name)
    data_ID = (var_id + (group_id << 10)).to_bytes(2,byteorder='big')
    data = bytes(formatted_name,'ascii')

    frame = bytearray()
    frame.append(0x00)
    frame += data_ID
    frame.append(fmt)
    frame += data

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc

    # Testing frame
    response = distantio.process(frame)

    assert response['type'] == 'returned-descriptor'
    assert response['var-id'] == var_id
    assert response['var-name'] == formatted_name
    assert response['var-type'] == fmt
    assert response['var-writeable'] == False
    assert response['var-group'] == group_id

def test_returned_descriptor_variable_writeable():
    distantio = distantio_protocol()

    # inputs
    var_id = 999
    name = "testvariable 2"
    fmt = 0xF3

    # formatting
    formatted_name = "{:14s}".format(name)
    v = (var_id).to_bytes(2,byteorder='big')
    n = bytes(formatted_name,'ascii')

    frame = bytearray()
    frame.append(0x00)
    frame += v
    frame.append(fmt)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-descriptor'
    assert response['var-id'] == var_id
    assert response['var-name'] == formatted_name
    assert response['var-type'] ==  fmt & 0x0F
    assert response['var-writeable'] == True

def test_returned_value_float():
    distantio = distantio_protocol()

    # inputs
    var_id = 124
    fmt = 0
    value = 1.362e-12
    extraid_1 = 1.25
    extraid_2 = 12715

    # formatting
    v = (var_id).to_bytes(2,byteorder='big')
    n = pack(distantio.format_lookup[fmt],value)

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(fmt)
    frame += pack('>f',extraid_1)
    frame += pack('>H',extraid_2)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-value'
    assert response['var-id'] == var_id
    assert round(response['var-value'],5) == round(value,5)
    assert response['var-type'] == fmt
    assert round(response['var-time'],5) == round(extraid_1,5)
    assert response['var-array-index'] == extraid_2

"""
# Not implemented yet, probably not worth it
def test_returned_value_float_in_group():
    distantio = distantio_protocol()

    # inputs
    # var id 124
    # group id 0xe
    var_id = 124
    group_id = 0xe
    formatted_id = ((group_id & 0x3F) << 10) + var_id
    fmt = 0
    value = 1.362e-12

    extraid_1 = 2.725
    extraid_2 = 9513

    # formatting
    v = (formatted_id).to_bytes(2,byteorder='big')
    n = pack(distantio.format_lookup[fmt],value)

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(fmt)
    frame += pack('>f',extraid_1)
    frame += pack('>H',extraid_2)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-value'
    assert response['var-id'] == var_id
    assert response['var-group'] == group_id
    assert round(response['var-value'],5) == round(value,5)
    assert response['var-type'] == fmt
    assert round(response['var-time'],5) == round(extraid_1,5)
    assert response['var-array-index'] == extraid_2
"""

def test_decode_int():
    distantio = distantio_protocol()

    # inputs
    var_id = 124
    group_id = 37
    fmt = 3
    value = 126594521
    extraid_1 = 2.725
    extraid_2 = 9513

    # formatting
    v = (var_id + (group_id<<10)).to_bytes(2,byteorder='big')
    n = pack(distantio.format_lookup[fmt],value)

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(fmt)
    frame += pack('>f',extraid_1)
    frame += pack('>H',extraid_2)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-value'
    assert response['var-id'] == var_id
    assert response['var-value'] == value
    assert response['var-type'] == fmt
    assert round(response['var-time'],5) == round(extraid_1,5)
    assert response['var-array-index'] == extraid_2

def test_returned_value_writeable_int():
    distantio = distantio_protocol()

    # inputs
    var_id = 124
    fmt = 0xF3
    value = 126594521
    extraid_1 = 2.725
    extraid_2 = 9513

    # formatting
    v = (var_id).to_bytes(2,byteorder='big')
    n = pack(distantio.format_lookup[fmt & 0x0F],value)

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(fmt)
    frame += pack('>f',extraid_1)
    frame += pack('>H',extraid_2)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-value'
    assert response['var-id'] == var_id
    assert response['var-value'] == value
    assert response['var-type'] == fmt & 0x0F
    assert round(response['var-time'],5) == round(extraid_1,5)
    assert response['var-array-index'] == extraid_2

def test_decode_group_descriptor():
    distantio = distantio_protocol()

    # inputs
    group_id = 39
    fmt = 0x07
    name = "testvar"

    # formatting
    formatted_name = "{:14s}".format(name)
    n = bytes(formatted_name,'ascii')

    # formatting
    v = (group_id << 10).to_bytes(2,byteorder='big')


    frame = bytearray()
    frame.append(0x00)
    frame += v
    frame.append(fmt)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-group-descriptor'
    assert response['group-id'] == group_id
    assert response['group-name'] == formatted_name

# test decoding valid alive-signal frame
def test_alive_signal():
    distantio = distantio_protocol()

    frame = bytearray(18)
    frame[0] = 0x03
    crc = crc16(frame).to_bytes(2,byteorder='big')
    frame += crc

    response = distantio.process(frame)

    assert response['type'] == 'alive-signal'

def test_decode_wrong_crc():
    distantio = distantio_protocol()

    var_id = (38153).to_bytes(2,byteorder='big')
    n = bytes("{:14s}".format("testvar"),'ascii')

    frame = bytearray()
    frame.append(0x00)
    frame += var_id
    frame.append(0x00)
    frame += n

    crc = (12238).to_bytes(2,byteorder='big')

    frame += crc

    assert pytest.raises(ValueError,distantio.process,frame)

def test_returned_descriptor_wrong_size():
    distantio = distantio_protocol()

    var_id = (38153).to_bytes(2,byteorder='big')
    n = bytes("{:14s}".format("testvar"),'ascii')

    frame = bytearray()
    frame.append(0x00)
    frame += var_id
    frame.append(0x00)
    frame += n

    assert pytest.raises(IndexError,distantio.process,frame)

def test_returned_descriptor_wrong_format():
    distantio = distantio_protocol()

    var_id = 38153
    name = "testvar"
    formatted_name = "{:14s}".format(name)

    v = (var_id).to_bytes(2,byteorder='big')
    n = bytes(formatted_name,'ascii')

    frame = bytearray()
    frame.append(0x00)
    frame += v
    frame.append(0xFF)# Wrong format
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')
    frame += crc

    assert pytest.raises(ValueError,distantio.process,frame)

def test_returned_value_wrong_format():
    distantio = distantio_protocol()

    var_id = 38153
    name = "testvariable 3"
    formatted_name = "{:14s}".format(name)

    v = (var_id).to_bytes(2,byteorder='big')
    n = bytes(formatted_name,'ascii')

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(0xFF)# Wrong format
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')
    frame += crc

    assert pytest.raises(ValueError,distantio.process,frame)

def test_decode_wrong_cmd():
    distantio = distantio_protocol()

    var_id = 38153
    name = "testvariable 1"
    formatted_name = "{:14s}".format(name)

    v = (var_id).to_bytes(2,byteorder='big')
    n = bytes(formatted_name,'ascii')

    frame = bytearray()
    frame.append(0xFF)# Wrong command
    frame += v
    frame.append(0x00)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')
    frame += crc

    assert pytest.raises(ValueError,distantio.process,frame)
