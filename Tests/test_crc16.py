# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# See __init__.py file on how to run tests automatically

from distantio.crc import crc16

def test_crc_single_bit_changed():
    data_a = [0x3f,0x1a,0xff,0x56,0x3a]
    crc_a = crc16(data_a)

    data_b = [0x3f,0x1a,0xef,0x56,0x3a]
    crc_b = crc16(data_b)

    assert crc_a != crc_b

def test_crc_know_value():
    # test the alive-signal from DistantIO
    data = [0x03,0x00,0x00,0x00,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17]
    crc = crc16(data)

    assert crc == 13216
