# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# See __init__.py file on how to run tests automatically

from DistantIO.API.distantio_protocol import distantio_protocol
from DistantIO.API.crc import crc16
from struct import pack,unpack
import pytest

# test encoding write-value command
"""
def test_encode_0x04_float():

    def rx(c):
        pass

    distantio = distantio_protocol(rx)
    frame = distantio.get_write_variable_frame(328,0,1.2687e13)

    assert
    print(frame)
"""
