
#ifndef _HELPERS_H_
#define _HELPERS_H


// Static type definitions
typedef uint8_t             pin;            // Hardware pins
typedef unsigned long       ptr;            // Pointers

// Dynamic array length calculation
#define array_len(ARR) (sizeof(ARR) / sizeof(ARR[0]))


#endif // _HELPERS_H_