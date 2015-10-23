# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# See __init__.py file on how to run tests automatically

from distantio.Datalogger import Datalogger
import pytest
import random
import numpy as np
import time

def test_datalogger_basic():
    d = Datalogger()

    for i in range(100):
        for j in range(2):
            value = i * 0.01 * j
            d.append('ea',float(i*0.01),j,value)

    d.export()

def test_datalogger_random_arrival():
    d = Datalogger()

    table = np.arange(100)
    random.shuffle(table)

    for i in table:
        for j in range(2):
            value = i * 0.01 * j
            d.append('ea',float(i*0.01),j,value)

    d.export()

def test_datalogger_multiple():
    d = Datalogger()

    for i in range(100):
        for j in range(2):
            value = i * 0.01 * j
            d.append('ea',float(i*0.01),j,value)

    for i in range(100):
        for j in range(5):
            value = i * 0.01 * j
            d.append('ba',float(i*0.01),j,value)

    d.export()

def test_datalogger_unauthorized_name():
    d = Datalogger()

    table = np.arange(100)
    random.shuffle(table)
    for i in table:
        for j in range(2):
            value = i * 0.01 * j
            d.append('\[',float(i*0.01),j,value)

    d.export()
