// Copyright (C) 2015 Rémi Bèges
// For conditions of distribution and use, see copyright notice in the LICENSE.md file

#ifndef SERIAL_PROTOCOL_H_
#define SERIAL_PROTOCOL_H_

#include <stdint.h>

#define ENCODING_BUFFER_SIZE 64
#define DECODING_BUFFER_SIZE 256

typedef void (*callback_t)(uint8_t* data, uint16_t size);

void init_protocol(void (*encoding_done_callback)(uint8_t*,uint16_t),void (*decoding_done_callback)(uint8_t*,uint16_t));
/*
 * Encodes new data with byte stuffing algorithm to delimit frame.
 * @input framedata : the raw data to process
 * @input framesize : size of the raw data to process (amount of bytes)
 */
void encode(uint8_t* framedata, uint16_t framesize);

/*
 * Append new byte to current decoding sequence. If a valid frame is detected,
 * the decoding_done_callback function is called and the valid frame is sent as parameter
 * @input received_byte : the new byte to add to the current decoding sequence
 */
void decode(uint8_t received_byte);

#endif /* SERIAL_PROTOCOL_H_ */
