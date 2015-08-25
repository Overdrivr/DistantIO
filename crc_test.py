from API.crc import *

packet = bytearray(12)

packet[0] = 0x02
packet[4] = 0xFF
packet[11] = 0xFF
print(packet)
crc = crc16(packet).to_bytes(2,byteorder='big')
print(crc)
