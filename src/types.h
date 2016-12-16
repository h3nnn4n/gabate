#ifndef TYPES_H
#define TYPES_H

#include <stdint.h>

typedef struct {
    uint8_t z  ; // Zero flag
    uint8_t n  ; // Subtraction bit ?
    uint8_t h  ; // Half carry bit
    uint8_t c  ; // Carry bit
} _cpu_flags;

typedef struct {
    unsigned char *memory;
    unsigned char enable_interrupts;

    unsigned long long cycles;
    unsigned long long instructions_executed;

    _cpu_flags flags;

    uint16_t pc;
    uint16_t sp;

    uint8_t portin0;
    uint8_t portin1;
    uint8_t portin2;

    uint16_t interrupt_addr;
    uint16_t shift_offset;
    uint16_t shift0;
    uint16_t shift1;

    uint8_t a;
    uint8_t b;
    uint8_t c;
    uint8_t d;
    uint8_t e;
    uint8_t h;
    uint8_t l;
} _cpu_info;

#endif /* TYPES_H */
