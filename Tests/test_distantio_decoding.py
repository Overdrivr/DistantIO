# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# See __init__.py file on how to run tests automatically

from DistantIO.API.distantio_protocol import distantio_protocol
from DistantIO.API.crc import crc16
from struct import pack,unpack
import pytest
# test decoding unkown command

# test decoding valid returned-descriptor frame
def test_decode_0x00():
    distantio = distantio_protocol()

    # inputs
    var_id = 999
    group_id = 18
    name = "testvar"
    fmt = 3

    # formatting
    formatted_name = "{:8s}".format(name)
    v = (var_id + (group_id << 10)).to_bytes(2,byteorder='big')
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
    assert response['var-type'] == fmt
    assert response['var-writeable'] == False
    assert response['var-group'] == group_id

def test_decode_0x00_writeable():
    distantio = distantio_protocol()

    # inputs
    var_id = 999
    name = "testvar"
    fmt = 0xF3

    # formatting
    formatted_name = "{:8s}".format(name)
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

def test_decode_float():
    distantio = distantio_protocol()

    # inputs
    var_id = 124
    fmt = 0
    value = 1.362e-12

    # formatting
    v = (var_id).to_bytes(2,byteorder='big')
    n = pack(distantio.format_lookup[fmt],value)

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(fmt)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-value'
    assert response['var-id'] == var_id
    assert round(response['var-value'],5) == round(value,5)
    assert response['var-type'] == fmt

def test_decode_float_in_group():
    distantio = distantio_protocol()

    # inputs
    # var id 124
    # group id 0xe
    var_id = 124
    var_group = 0xe
    formatted_id = ((var_group & 0x3F) << 10) + var_id
    fmt = 0
    value = 1.362e-12

    # formatting
    v = (formatted_id).to_bytes(2,byteorder='big')
    n = pack(distantio.format_lookup[fmt],value)

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(fmt)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-value'
    assert response['var-id'] == var_id
    #assert response['var-group'] == 0xe
    assert round(response['var-value'],5) == round(value,5)
    assert response['var-type'] == fmt

def test_decode_int():
    distantio = distantio_protocol()

    # inputs
    var_id = 124
    group_id = 37
    fmt = 3
    value = 126594521

    # formatting
    v = (var_id + (group_id<<10)).to_bytes(2,byteorder='big')
    n = pack(distantio.format_lookup[fmt],value)

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(fmt)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-value'
    assert response['var-id'] == var_id
    assert response['var-value'] == value
    assert response['var-type'] == fmt

def test_decode_writeable_int():
    distantio = distantio_protocol()

    # inputs
    var_id = 124
    fmt = 0xF3
    value = 126594521

    # formatting
    v = (var_id).to_bytes(2,byteorder='big')
    n = pack(distantio.format_lookup[fmt & 0x0F],value)

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(fmt)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    response = distantio.process(frame)

    assert response['type'] == 'returned-value'
    assert response['var-id'] == var_id
    assert response['var-value'] == value
    assert response['var-type'] == fmt & 0x0F

def test_decode_group_descriptor():
    distantio = distantio_protocol()

    # inputs
    group_id = 39
    fmt = 0x07
    name = "testvar"

    # formatting
    formatted_name = "{:8s}".format(name)
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
def test_decode_0x03():
    distantio = distantio_protocol()

    data = [0x03,0x00,0x00,0x00,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17]
    frame = bytearray(data)
    crc = crc16(frame).to_bytes(2,byteorder='big')
    frame += crc

    response = distantio.process(frame)

    assert response['type'] == 'alive-signal'

def test_decode_wrong_crc():
    distantio = distantio_protocol()

    var_id = (38153).to_bytes(2,byteorder='big')
    n = bytes("{:8s}".format("testvar"),'ascii')

    frame = bytearray()
    frame.append(0x00)
    frame += var_id
    frame.append(0x00)
    frame += n

    crc = (12238).to_bytes(2,byteorder='big')

    frame += crc

    assert pytest.raises(ValueError,distantio.process,frame)

def test_decode_wrong_size():
    distantio = distantio_protocol()

    var_id = (38153).to_bytes(2,byteorder='big')
    n = bytes("{:8s}".format("testvar"),'ascii')

    frame = bytearray()
    frame.append(0x00)
    frame += var_id
    frame.append(0x00)
    frame += n

    assert pytest.raises(IndexError,distantio.process,frame)

def test_decode_wrong_format_0x00():
    distantio = distantio_protocol()

    var_id = 38153
    name = "testvar"
    formatted_name = "{:8s}".format(name)

    v = (var_id).to_bytes(2,byteorder='big')
    n = bytes(formatted_name,'ascii')

    frame = bytearray()
    frame.append(0x00)
    frame += v
    frame.append(0x09)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')
    frame += crc

    assert pytest.raises(ValueError,distantio.process,frame)

def test_decode_wrong_format_0x01():
    distantio = distantio_protocol()

    var_id = 38153
    name = "testvar"
    formatted_name = "{:8s}".format(name)

    v = (var_id).to_bytes(2,byteorder='big')
    n = bytes(formatted_name,'ascii')

    frame = bytearray()
    frame.append(0x01)
    frame += v
    frame.append(0x09)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')
    frame += crc

    assert pytest.raises(ValueError,distantio.process,frame)

def test_decode_wrong_cmd():
    distantio = distantio_protocol()

    var_id = 38153
    name = "testvar"
    formatted_name = "{:8s}".format(name)

    v = (var_id).to_bytes(2,byteorder='big')
    n = bytes(formatted_name,'ascii')

    frame = bytearray()
    frame.append(0x09)
    frame += v
    frame.append(0x00)
    frame += n

    crc = crc16(frame).to_bytes(2,byteorder='big')
    frame += crc

    assert pytest.raises(ValueError,distantio.process,frame)
