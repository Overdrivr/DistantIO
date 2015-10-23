# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# See __init__.py file on how to run tests automatically

from distantio.DistantioProtocol import distantio_protocol
from distantio.crc import crc16
from struct import pack,unpack
import pytest
