//From : https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks

#ifndef CRC_H_
#define CRC_H_

#include <stdint.h>

uint16_t crc16(uint8_t *data, uint16_t len);

#endif
