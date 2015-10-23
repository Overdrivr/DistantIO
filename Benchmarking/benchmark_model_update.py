# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# See __init__.py file on how to run tests automatically

from distantio import DistantIO
from distantio import distantio_protocol
from distantio import crc16
from struct import pack
from time import time
import logging
import cProfile, pstats, io

# First update algorithm with testing queue.empty
# 100 000 instructions : 13 seconds

# Second update algorithm with try except on queue.get
# 100 000 instructions : 9-14 seconds

# Third algorithm

def encode_test_frame(variable_id, group_id, extraid_1,extraid_2, value, fmt, fmtlookup):
    # formatting
    data_ID = (variable_id + (group_id << 10)).to_bytes(2,byteorder='big')
    data = pack(fmtlookup[fmt],value)

    frame = bytearray()
    frame.append(0x01)
    frame += data_ID
    frame.append(fmt)
    frame += data
    frame += pack('>f',extraid_1)
    frame += pack('>H',extraid_2)

    crc = crc16(frame).to_bytes(2,byteorder='big')

    frame += crc
    return frame

if __name__ == '__main__':

    # Instanciate API
    model = DistantIO()

    # Deactivate logging
    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)

    # Instanciate a decoder to generate test instruction
    decoder = distantio_protocol()

    # Create test data
    f = encode_test_frame(999,1,0.0,0,1.12345e2,0,decoder.format_lookup)
    instruction = decoder.process(f)


    # Inject test data
    amount = 100000
    for i in range(amount):
        model.output_queue.put(instruction)



    pr = cProfile.Profile()
    pr.enable()

    # Start test
    start = time()
    for i in range(amount):
        model.update()

    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    ps.dump_stats("Benchmarking/progiling_at_.log")
    print(s.getvalue())



    elapsed = time() - start
    print("Elapsed time (s) : ",elapsed)
    model.terminate()
