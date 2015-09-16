// Copyright (C) 2015 Rémi Bèges
// For conditions of distribution and use, see copyright notice in the LICENSE.md file

/*
 * WARNING : IMPLEMENTATION FOR LITTLE-ENDIAN PROCESSOR
 * TODO : HANDLE BOTH
 */

#ifndef DISTANTIO_H_
#define DISTANTIO_H_

#include <stdint.h>

#define PAYLOAD_SIZE 14
#define DATA_SIZE 8
#define VARIABLES_AMOUNT 256
#define GROUPS_AMOUNT 128

typedef enum dio_type dio_type;
enum dio_type
{
	dio_type_FLOAT = 0x00,
	dio_type_UINT8 = 0x01,
	dio_type_UINT16 = 0x02,
	dio_type_UINT32 = 0x03,
	dio_type_INT8 = 0x04,
	dio_type_INT16 = 0x05,
	dio_type_INT32 = 0x06,
};

typedef struct variable variable;
struct variable
{
	uint8_t* ptr;
	uint16_t size;
	uint8_t writeable;
	uint16_t id;
	dio_type type;
	char name[8];
	uint8_t send;
	uint8_t groupID;
};

typedef struct group group;
struct group
{
	char name[8];
	uint8_t groupID;
};

//typedef struct log log;
struct log
{
	variable variables[VARIABLES_AMOUNT];
	group groups[GROUPS_AMOUNT];
	uint16_t amount;
	uint8_t current_group_id;
};

void init_distantio();

uint8_t register_var(void* ptr, uint16_t size, dio_type type, uint8_t writeable, char* name);
void start_group(char* groupname);

void distantio_decode(uint8_t* data,uint16_t datasize);

// To call often
void send_variables();
void send_alive();

#endif /* DISTANTIO_H_ */
