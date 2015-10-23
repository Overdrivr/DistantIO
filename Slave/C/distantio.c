/*
 * distantio.c
 *
 *  Created on: Oct 13, 2014
 *      Author: B48923
 */

#include "distantio.h"
#include "crc.h"
#include "string.h"
#include "protocol.h"

/*
 * WARNING : IMPLEMENTATION FOR LITTLE-ENDIAN PROCESSOR
 * TODO : HANDLE BOTH
 */

static log Log;
uint32_t tmp;

void _dIO_send_variable(uint16_t index,float extra_identifier_1,uint16_t extra_identifier_2=0);
uint16_t _dIO_get_size(dio_type type);
void _dIO_send_descriptor(uint16_t index);
void _dIO_send_group_descriptor(uint16_t index);


void dIO_init()
{
	uint16_t i;
	char default_name[] = {"undef.  "};
	Log.amount = 0;
	for(i = 0 ; i < VARIABLES_AMOUNT ; i++)
	{
		Log.variables[i].size = 0;
		Log.variables[i].ptr = 0;
		Log.variables[i].writeable = 0;
		Log.variables[i].id = i;
		strncpy(Log.variables[i].name,default_name,NAMESIZE);
		Log.variables[i].send = 0;
		Log.variables[i].groupID = 0;
	}
	tmp=0;
	Log.current_group_id = 0;
	strncpy(Log.groups[0].name,"default",NAMESIZE);
}

uint8_t dIO_var(void* ptr, uint16_t size, dio_type type, uint8_t writeable, char* name, float refresh_rate)
{
	// Too many variables, aborting
	if(Log.amount >= VARIABLES_AMOUNT)
		return 1;

	Log.variables[Log.amount].ptr = (uint8_t*) ptr;
	Log.variables[Log.amount].size = _dIO_get_size(type);
	Log.variables[Log.amount].writeable = writeable;
	Log.variables[Log.amount].type = type;
	Log.variables[Log.amount].groupID = Log.current_group_id;
	strncpy(Log.variables[Log.amount].name,name,NAMESIZE);
	Log.variables[Log.amount].refresh_rate = refresh_rate;
	Log.variables[Log.amount].last_refreshed = 0;
	Log.amount++;

	return 0;
}

void dIO_group(char* groupname)
{
	Log.current_group_id++;
	strncpy(Log.groups[Log.current_group_id].name,groupname,NAMESIZE);
}

void dIO_decode(uint8_t* data,uint16_t datasize)
{
	// First check data size
	if(datasize != FRAMESIZE)
		return;

	// Second, check CRC
	uint16_t crc_value = crc16(data,FRAMESIZE-2);
	uint16_t crc_rx = ((uint16_t)data[FRAMESIZE-2] << 8) | data[FRAMESIZE-1];

	if(crc_value != crc_rx)
		return;

	// Process frame
	// First, identify command
	uint8_t command = data[0];

	// Second, identify variable ID
	uint16_t ID = data[2] + (data[1] << 8);
	ID = (ID & 0x3FF);

	// Third, identify data type
	uint8_t type = data[3];

	switch(command)
	{
		// User requested descriptors
		case 0x02:
			// Send variables
			for(uint16_t i = 0 ; i < Log.amount ; i++)
				_dIO_send_descriptor(i);
			// Send groups
			for(uint16_t i = 0 ; i <= Log.current_group_id ; i++)
				_dIO_send_group_descriptor(i);
			break;

		// User provided value to write
		case 0x04:
			if(ID >= Log.amount)
				return;

			if(Log.variables[ID].writeable == 0x00)
				return;

			if(Log.variables[ID].type != type)
				return;

			uint16_t start_address = DATASTART + DATASIZE - 1;

			// Copy contents directly into variable
			for(uint16_t i = 0 ; i < Log.variables[ID].size ; i++)
			{
				// Packet is big-endian, convert to little-endian
				uint8_t offset = start_address - i;
				*(Log.variables[ID].ptr + i) = *(data + offset);
			}
			break;

		// User requested variable read
		case 0x05:
			if(ID >= Log.amount)
				return;

			Log.variables[ID].send = 1;
			break;

		// User requested stop variable read
		case 0x06:
			if(ID >= Log.amount)
				return;
			Log.variables[ID].send = 0;
			break;

	}
}

void dIO_update(float current_time)
{
	for(uint16_t i = 0 ; i < Log.amount ; i++)
	{
		if(Log.variables[i].send == 0)
			continue;

		if(current_time < Log.variables[i].last_refreshed + Log.variables[i].refresh_rate)
			continue;

		_dIO_send_variable(i,current_time);
		Log.variables[i].last_refreshed = current_time;
	}
}

void dIO_send_alive()
{
	uint8_t buffer[FRAMESIZE];
	buffer[0] = 0x03;

	// Compute crc
	uint16_t crc_value = crc16(buffer,FRAMESIZE - 2);

	// Write crc into buffer's last byte
	buffer[FRAMESIZE - 1] = crc_value & 0xFF;
	buffer[FRAMESIZE - 2] = (crc_value >> 8) & 0xFF;

	// Send frame to encoding
	encode(buffer,FRAMESIZE);
}

 void dIO_emergency_send(void* ptr, uint16_t size, dio_type type, char* name, float recordingtime, uint16_t index)
 {

	uint8_t buffer[FRAMESIZE];

	// Response code 0x09
	buffer[0] = 0x09;

	// Write variable ID
	uint8_t * temp_ptr = (uint8_t*)(name);
	buffer[1] = *(temp_ptr + 1);
	buffer[2] = *(temp_ptr);

	// Write variable type
	buffer[3] = type;

	// Extra identifier 1
	temp_ptr = (uint8_t*)(&recordingtime);
	buffer[4] = *(temp_ptr + 3);
	buffer[5] = *(temp_ptr + 2);
	buffer[6] = *(temp_ptr + 1);
	buffer[7] = *(temp_ptr    );

	// Extra identifier 2
	temp_ptr = (uint8_t*)(&index);
	buffer[8] = *(temp_ptr + 1);
	buffer[9] = *(temp_ptr    );

	uint16_t i = 10;

	// Write data
	for(uint16_t k = 0 ; k < DATASIZE ; k++)
	{
		uint16_t off = DATASIZE - 1 - k;

		// Fill buffer with data
		if(off < size)
		{
			temp_ptr = (uint8_t*)(ptr) + off ;
			buffer[i++] = *temp_ptr;
		}
		// Fill remaining bits with 0
		else
		{
			buffer[i++] = 0;
		}
	}

	// Compute crc
	uint16_t crc_value = crc16(buffer,i);

	// Write crc into buffer's last byte
	buffer[i++] = (crc_value >> 8) & 0xFF;
	buffer[i++] = crc_value & 0xFF;

	// Encode frame
	encode(buffer,i);
 }

/* ------------------- PRIVATE FUNCTIONS ------------------ */

void _dIO_send_descriptor(uint16_t index)
{
	if(index >= Log.amount)
		return;

	uint8_t buffer[FRAMESIZE];
	uint8_t type;

	// Respond returned-descriptor
	buffer[0] = 0x00;

	// Write id
	uint16_t ID = ((Log.variables[index].groupID & 0x003F) << 10) + (index & 0x3FF);
	uint8_t * temp_ptr = (uint8_t*)(&ID);
	buffer[1] = *(temp_ptr + 1);
	buffer[2] = *(temp_ptr    );

	// Write type & writeable

	type = (uint8_t)(Log.variables[index].type);

	if(Log.variables[index].writeable)
		type += 0xF0;

	buffer[3] = type;

	//Write name
	uint16_t i = 4;
	// TODO : Replace with strncpy
	for(uint16_t k = 0 ; k < NAMESIZE ; k++)
	{
		if(k < strlen(Log.variables[index].name))
		{
			buffer[i] = Log.variables[index].name[k];
			i++;
		}
		else
			buffer[i++] = 0;
	}

	// Compute crc
	uint16_t crc_value = crc16(buffer,i);

	// Write crc into buffer's last byte
	buffer[i++] = (crc_value >> 8) & 0xFF;
	buffer[i++] = crc_value & 0xFF;

	// Encode frame
	encode(buffer,i);
}

void _dIO_send_group_descriptor(uint16_t index)
{
	if(index > Log.current_group_id)
		return;

	uint8_t buffer[FRAMESIZE];

	// Respond returned-descriptor
	buffer[0] = 0x00;

	// Write id
	uint16_t ID = (index & 0x3F) << 10;
	uint8_t * temp_ptr = (uint8_t*)(&ID);
	buffer[1] = *(temp_ptr + 1);
	buffer[2] = *(temp_ptr);

	// Write type
	buffer[3] = 0x07;

	//Write name
	uint16_t i = 4;
	for(uint16_t k = 0 ; k < NAMESIZE ; k++)
	{
		if(k < strlen(Log.groups[index].name))
		{
			buffer[i] = Log.groups[index].name[k];
			i++;
		}
		else
			buffer[i++] = 0;
	}

	// Compute crc
	uint16_t crc_value = crc16(buffer,i);

	// Write crc into buffer's last byte
	buffer[i++] = (crc_value >> 8) & 0xFF;
	buffer[i++] = crc_value & 0xFF;

	// Encode frame
	encode(buffer,i);
}


void _dIO_send_variable(uint16_t index,float extra_identifier_1,uint16_t extra_identifier_2)
{
	if(index >= Log.amount)
		return;

	uint8_t buffer[FRAMESIZE];

	// Response code 0x01
	buffer[0] = 0x01;

	// Write variable ID
	uint16_t ID = ((Log.variables[index].groupID & 0x003F) << 10) + (index & 0x3FF);
	uint8_t * temp_ptr = (uint8_t*)(&ID);
	buffer[1] = *(temp_ptr + 1);
	buffer[2] = *(temp_ptr);

	// Write variable type
	buffer[3] = Log.variables[index].type;
	//TODO writeable

	// Extra identifier 1
	temp_ptr = (uint8_t*)(&extra_identifier_1);
	buffer[4] = *(temp_ptr + 3);
	buffer[5] = *(temp_ptr + 2);
	buffer[6] = *(temp_ptr + 1);
	buffer[7] = *(temp_ptr    );

	// Extra identifier 2
	temp_ptr = (uint8_t*)(&extra_identifier_2);
	buffer[8] = *(temp_ptr + 1);
	buffer[9] = *(temp_ptr    );

	uint16_t i = 10;

	// Write data
	for(uint16_t k = 0 ; k < DATASIZE ; k++)
	{
		uint16_t off = DATASIZE - 1 - k;

		// Fill buffer with data
		if(off < Log.variables[index].size)
		{
			temp_ptr = Log.variables[index].ptr + off ;
			buffer[i++] = *temp_ptr;
		}
		// Fill remaining bits with 0
		else
		{
			buffer[i++] = 0;
		}
	}

	// Compute crc
	uint16_t crc_value = crc16(buffer,i);

	// Write crc into buffer's last byte
	buffer[i++] = (crc_value >> 8) & 0xFF;
	buffer[i++] = crc_value & 0xFF;

	// Encode frame
	encode(buffer,i);
}


uint16_t _dIO_get_size(dio_type type)
{
	switch(type)
	{
		case dio_type_FLOAT:
		case dio_type_UINT32:
		case dio_type_INT32:
			return 4;

		case dio_type_UINT16:
		case dio_type_INT16:
			return 2;

		case dio_type_UINT8:
		case dio_type_INT8:
		default:
			return 1;
	}
}
