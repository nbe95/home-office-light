// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_MACROS_H_
#define SRC_MACROS_H_


// Dynamic array length calculation
#define ARRAY_LEN(ARR) (sizeof(ARR) / sizeof(ARR[0]))


// Useful bit operations and bitfield macros
#define BIT(n)                      (1 << (n))
#define BIT_SET(y, mask)            (y |=  (mask))
#define BIT_CLEAR(y, mask)          (y &= ~(mask))
#define BIT_FLIP(y, mask)           (y ^=  (mask))
#define BIT_MASK(len)               (BIT(len) - 1)                                                  // Create bitmask of given length
#define BF_MASK(start, len)         (BIT_MASK(len) << (start))                                      // Create a bitfield mask starting at an offset
#define BF_PREP(x, start, len)      (((x) & BIT_MASK(len)) << (start))                              // Prepare a bitmask for insertion or combining
#define BF_GET(y, start, len)       (((y) >> (start)) & BIT_MASK(len))                              // Extract a bitfield of a given length starting at a given offset
#define BF_SET(y, x, start, len)    (y = ((y) & ~BF_MASK(start, len)) | BF_PREP(x, start, len))     // Insert a value into an existing bitfield


#endif  // SRC_MACROS_H_
