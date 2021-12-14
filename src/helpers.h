#ifndef SRC_HELPERS_H_
#define SRC_HELPERS_H_

// Include necessary headers
#include "./timer.h"


// Static type definitions
typedef uint16_t    knx_addr;   // KNX addresses
typedef uint8_t     pin;        // Hardware pins
typedef uint32_t    ptr;        // Pointer

// Dynamic array length calculation
#define array_len(ARR) (sizeof(ARR) / sizeof(ARR[0]))


#endif  // SRC_HELPERS_H_
