/******************************************************************************
 * Copyright (C) 2016  Renan S. Silva                                         *
 *                                                                            *
 * This software is provided 'as-is', without any express or implied          *
 * warranty. In no event will the authors be held liable for any damages      *
 * arising from the use of this software.                                     *
 *                                                                            *
 * Permission is granted to anyone to use this software for any purpose,      *
 * including commercial applications, and to alter it and redistribute it     *
 * freely, subject to the following restrictions:                             *
 *                                                                            *
 * 1. The origin of this software must not be misrepresented; you must not    *
 *    claim that you wrote the original software. If you use this software    *
 *    in a product, an acknowledgment in the product documentation would be   *
 *    appreciated but is not required.                                        *
 * 2. Altered source versions must be plainly marked as such, and must not be *
 *    misrepresented as being the original software.                          *
 * 3. This notice may not be removed or altered from any source distribution. *
 ******************************************************************************/
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#include <sys/types.h>

#include "agent.h"
#include "automated_tests.h"
#include "cartridge.h"
#include "decoder.h"
#include "disassembler.h"
#include "display.h"
#include "file_control.h"
#include "graphics.h"
#include "memory.h"
#include "other_window.h"
#include "results.h"
#include "rev.h"
#include "settings.h"
#include "time_keeper.h"
#include "types.h"
#include "utils.h"

int main(int argc, char *argv[]) {
    if (argc < 3)
        fprintf(stderr, "Missing argument\n");

    load_settings(argv[2]);

    _cpu_info cpu;
    sdl_init();

    srand48(mix(clock(), time(NULL), getpid()));
    srand(mix(clock(), time(NULL), getpid()));

    other_window_init();
    atexit(sdl_quit);

    init_cpu(&cpu);
    init_file_control();

    load_rom(&cpu, argv[1], 0x0000);
    check_rom(&cpu);

    /*print_rom_info(&cpu);*/

    reset_code_and_data();

    // FIXME: This needs a better api I think
    set_cpu_pointer(&cpu);

    if (pong())
        exit(EXIT_SUCCESS);

    while (ai_state.game_state != GAMEOVER) {
        decoder(&cpu);
    }

    print_agent_results();

    return EXIT_SUCCESS;
}
