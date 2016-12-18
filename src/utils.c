#include <sys/stat.h>
#include <sys/types.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>

#include "types.h"
#include "disassembler.h"

off_t fsize(const char *filename) {
    struct stat st;

    if (stat(filename, &st) == 0)
        return st.st_size;

    fprintf(stderr, "Cannot determine size of %s: %s\n", filename, strerror(errno));
return -1;
}

void init_cpu( _cpu_info *cpu ) {
    cpu->memory = calloc ( 1, 64 * 1024 ) ; // Allocs 64Kb of ram
    cpu->cycles = 0;
    cpu->pc     = 0;
    cpu->a      = 0;
    cpu->b      = 0;
    cpu->c      = 0;
    cpu->d      = 0;
    cpu->e      = 0;
    cpu->h      = 0;
    cpu->l      = 0;

    cpu->flags.z   = 0;
    cpu->flags.n   = 0;
    cpu->flags.h   = 0;
    cpu->flags.c   = 0;

    cpu->enable_interrupts     = 0;
    cpu->instructions_executed = 0;

    cpu->interrupt_addr = 0x10;
    cpu->interrupt_addr = 0x08;

    cpu->portin0 = 0x0e;
    cpu->portin1 = 0x08;
    cpu->portin2 = 0x00;

    cpu->pc = 0x100;
    cpu->sp = 0xfffe;

    cpu->a  = 0x01;
    cpu->b  = 0x00;
    cpu->c  = 0x13;
    cpu->d  = 0x00;
    cpu->e  = 0xd8;
    cpu->h  = 0x01;
    cpu->l  = 0x4d;

    cpu->flags.z = 1;
    cpu->flags.n = 0;
    cpu->flags.h = 1;
    cpu->flags.c = 1;

    cpu->memory[0xff10] = 0x80;
    cpu->memory[0xff11] = 0xbf;
    cpu->memory[0xff12] = 0xf3;
    cpu->memory[0xff14] = 0xbf;
    cpu->memory[0xff16] = 0x3f;
    cpu->memory[0xff19] = 0xbf;
    cpu->memory[0xff1a] = 0x7f;
    cpu->memory[0xff1b] = 0xff;
    cpu->memory[0xff1c] = 0x9f;
    cpu->memory[0xff1e] = 0xbf;
    cpu->memory[0xff20] = 0xff;
    cpu->memory[0xff23] = 0xbf;
    cpu->memory[0xff24] = 0x77;
    cpu->memory[0xff25] = 0xf3;
    cpu->memory[0xff26] = 0xf1;
    cpu->memory[0xff40] = 0x91;
    cpu->memory[0xff47] = 0xfc;
    cpu->memory[0xff48] = 0xff;
    cpu->memory[0xff49] = 0xff;
}

void unimplemented_opcode( _cpu_info *cpu ) {
    disassembler ( cpu->memory, cpu->pc );
    exit(-1);
}

int parity_bit ( int b ) {
    int bits = 0;
    int i    = 0;

    for (i = 0; i < 8; ++i)
        if ( b & ( 1 << i ) )
            bits += 1;

    return bits & 1 ? 0 : 1;
}

void print_registers ( _cpu_info *cpu ) {
    uint8_t f = ( (cpu->flags.z ) ? 0x80 : 0x00 ) |
                ( (cpu->flags.n ) ? 0x40 : 0x00 ) |
                ( (cpu->flags.h ) ? 0x20 : 0x00 ) |
                ( (cpu->flags.c ) ? 0x10 : 0x00 ) ;

    printf(" AF: %02x%02x BC: %02x%02x DE: %02x%02x HL: %02x%02x PC: %04x SP: %04x",
            cpu->a, f, cpu->b, cpu->c, cpu->d, cpu->e, cpu->h, cpu->l, cpu->pc, cpu->sp);
    printf(" F: %c%c%c%c CYCLES: %16llu IPS: %16llu\n",
            cpu->flags.z  ? 'z' : '.',
            cpu->flags.n  ? 'n' : '.',
            cpu->flags.h  ? 'h' : '.',
            cpu->flags.c  ? 'c' : '.',
            cpu->cycles              ,
            cpu->instructions_executed);
    /*printf(BYTE_TO_BINARY_PATTERN"\n", BYTE_TO_BINARY(f));*/
}
