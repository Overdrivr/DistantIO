# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

# Test of the protocol algorithm with dummy frames

from API.Protocol import Protocol

def build_rx_value():
    print("RX test started.")
    c = bytearray()
    #SOF
    c.append(int('f7',16))
    #CMD
    c.append(int('00',16))
    #DATATYPE
    c.append(int('00',16))
    #DATAID
    c.append(int('00',16))
    c.append(int('7D',16))#ESC EOF char
    c.append(int('7f',16))
    #VALUE
    c.append(int('05',16))
    c.append(int('7D',16))#ESC SOF char
    c.append(int('f7',16))
    c.append(int('E4',16))
    c.append(int('7D',16))#ESC ESC char
    c.append(int('7D',16))
    
    #EOF
    c.append(int('7f',16))

    print("RX :",c)
    
    return c

def build_tx_value():
    print("TX test started.")
    c = bytearray()
    
    #CMD
    c.append(int('00',16))
    #DATATYPE
    c.append(int('00',16))
    #DATAID
    c.append(int('00',16))
    c.append(int('7f',16))
    #VALUE
    c.append(int('05',16))
    c.append(int('f7',16))
    c.append(int('E4',16))
    c.append(int('7D',16))
    
    return c

def on_new_payload(rxpayload):
    print("TX :",rxpayload)


if __name__ == '__main__':
    # Create protocol and give callback function
    protocol = Protocol(on_new_payload)

    # Test to decode
    for c in build_rx_value():
        protocol.decode(c)

    # Test to encode
    tx = protocol.encode(build_tx_value())

    build_rx_value()
    print("TX :",tx)

print("Done.")
