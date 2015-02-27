# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

from API.Model import Model
from pubsub import pub
from threading import Timer

run = True

def stop():
    print("Stopping.")
    global run
    run = False
    

model = Model()
t = Timer(1.0, stop)
t.start()

model.start()

if model.connect_com("COM23") is False:
    print("Issue connecting")
    run = False

while(run):
    if not model.is_alive(1.0):
        print("Lost.")
    

print("Joining")
model.stop()
model.join()

print("Done.")
