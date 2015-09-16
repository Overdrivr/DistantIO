//From : https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks

#include "crc.h"

uint16_t crc16(uint8_t* data, uint16_t len)
{
	uint16_t rem  = 0;
	uint16_t n = 16;
	// A popular variant complements rem here
	for(uint16_t i = 0 ; i < len ; i++)
	{
		rem  = rem ^ (data[i] << (n-8));   // n = 16 in this example

		for(uint16_t j = 1 ; j < 8 ; j++)  // Assuming 8 bits per byte
		{

			if(rem & 0x8000)
			{
				// if leftmost (most significant) bit is set
				rem  = (rem << 1) ^ 0x1021;
			}
			else
			{
				rem  = rem << 1;
			}
		 rem  &= 0xffff;      // Trim remainder to 16 bits
		}
	}
 // A popular variant complements rem here
  return rem;
 }
