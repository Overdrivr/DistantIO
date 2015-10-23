/*
 * distantio.h
 *
 *  Created on: Oct 13, 2014
 *      Author: B48923
 */

#ifndef DISTANTIO_H_
#define DISTANTIO_H_

#include <stdint.h>

#define FRAMESIZE 20
#define DATASIZE 8
#define DATASTART 10
#define VARIABLES_AMOUNT 256
#define GROUPS_AMOUNT 128
#define NAMESIZE 14

/** Data types that can be exchanged effortlessly with the computer.
 *
 *
 */
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
	char name[NAMESIZE];
	uint8_t send;
	uint8_t groupID;
	float refresh_rate;
	float last_refreshed;
};

typedef struct group group;
struct group
{
	char name[NAMESIZE];
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

/** Initializes the DistantIO framework
 *  This is used to create the internal log
 *  @note Don't forget to initialize the frame delimiting protocol @see protocol.h
 *
 */
void dIO_init();

/** Registers a variable in the log. This function is usually called during program initalization
 *  All this data is stored in a descriptor that can be queried from master-side.
 *  @param ptr Pointer to the memory adress of the variable. Not extremely safe but that's all can be done with C
 *  @param size Size of the variable. Use sizeof(..) to always provide the right size. This will be improved when switching over C++ templated class
 *  @param type type of the variable. For a list of possible types @see dio_type
 *  @param writeable 0 if the variable is not writeable from master-side, 1 otherwise.
 *  @param name Name of the variable to identify the variable easily master-side. Names don't have to be uniques, and are limited to 14 characters.
 *  @param refresh_rate Time interval in seconds between two consecutive sends of the variable to the master. 0 means the variable is send on each call to @see dIO_update
 *  @returns
 		0 if everything ok
 		1 if the internal log is full.
 */
uint8_t dIO_var(void* ptr, uint16_t size, dio_type type, uint8_t writeable, char* name, float refresh_rate = 0);

/** Starts a new group. Any subsequent call to @dio_var will register the variable under this new group.
 *  Groups also have descriptors that can be queried from master-side.
 *	@param groupname name of the variable group. Limited to 14 characters.
 *
 */
void dIO_group(char* groupname);

/** Decodes the contents of a new received frame. Frame of unvalid sizes or with unvalid CRCs are immediatly discarded.
 *  @param data pointer to the data buffer start adress
 *  @param datasize size in bytes of the data buffer
 */
void dIO_decode(uint8_t* data,uint16_t datasize);

/** Updates the internal state of DistantIO. Variables will be sent upon calling this method.
 *  It is recommended to call this method approximately 10 times per second to keep impact on mbed device low while having good refresh rate master side.
 *  @note execution time of this function is directly related to the amount of registered variables, especially with small or 0 refresh rates.
 *  @param elapsed time since the beginning of the program
 *
 */
void dIO_update(float current_time);

/** Sends an alive signal to the master to signal the mbed device is running and communication is working.
 *  You should call this method approximately every half second.
 *
 */
void dIO_send_alive();

/** Manual mode for sending special data in case of particular events.
 *  This is useful to debug issues happening much faster than human perception, because this data will be exported master-side to an excel file.
 *  This mode can also support arrays by calling it for each array index and specifying that index as last parameter.
 *  Master-side, data is sorted in a hierchical manner, first by name, then by recording time, then by index (see parameters).
 *  @param ptr Pointer to the data start adress
 *  @param size Size in bytes of the data. Use sizeof(..) to avoid mistakes.
 *  @param type Type of the variable. For a list of possible types @see dio_type
 *  @param name Quick custom name for the variable. Limited to 2 characters for now.
 *  @param recordingtime User-specified field intented for associating a specific time with the data
 *  @param index User-specified field for associating a specific index to the data.
 */
 void dIO_emergency_send(void* ptr, uint16_t size, dio_type type, char* name, float recordingtime, uint16_t index = 0);

#endif /* DISTANTIO_H_ */
