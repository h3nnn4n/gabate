/******************************************************************************
 * Copyright (C) 2016-2017, 2025  Renan S. Silva                            *
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
#include <string.h>

#include "agent.h"
#include "feature_functions.h"
#include "feature_set.h"
#include "ff_controller.h"
#include "other_window.h"
#include "results.h"
#include "settings.h"
#include "stats.h"
#include "tetris.h"
#include "trainer.h"
#include "types.h"
#include "utils.h"


static _brain brain;
static _agent_params current_params;

void scaler() {
    for (int i = 0; i < ff_ctrl_current_plus(); ++i) {
        current_params.cost[i] *= current_params.weight[(i * GEN_P_FUNCTION) + 2];
    }
}

void evaluate_cost() {
    get_brain_pointer()->round_has_cleaned_lines = cleaned_any_row() ? 1 : 0;

    char *feature_set_name = get_agent_config()->feature_set_name;

    ff_ctrl_reset();

    if (strcmp(feature_set_name, "FBDP") == 0) {
        feature_set_FBDP();
    } else if (strcmp(feature_set_name, "NDP") == 0) {
        feature_set_NDP();
    } else if (strcmp(feature_set_name, "KBR") == 0) {
        feature_set_KBR();
    } else if (strcmp(feature_set_name, "CMA") == 0) {
        feature_set_CMA();
    } else if (strcmp(feature_set_name, "HA") == 0) {
        feature_set_HA();
    } else if (strcmp(feature_set_name, "LELmark") == 0) {
        feature_set_LELmark();
    } else if (strcmp(feature_set_name, "ALL") == 0) {
        feature_set_ALL();
    } else if (strcmp(feature_set_name, "HA2") == 0) {
        feature_set_HA2();
    } else if (strcmp(feature_set_name, "testing") == 0) {
        feature_set_testing();
    } else if (strcmp(feature_set_name, "basic") == 0) {
        feature_set_basic();
    } else {
        printf("Unknown feature set: %s\n", feature_set_name);
        abort();
    }


    scaler();
}

void initialize_agent() {
    const double *agent_weights = get_agent_weights();
    for (int j = 0; j < N_GENES; ++j) {
        current_params.weight[j] = agent_weights[j];
        current_params.cost[j] = 0;
    }
}


double get_cost() {
    double result = 0;
    for (int i = 0; i < ff_ctrl_current_plus(); i++) {
        result += current_params.cost[i];
    }
    return result;
}

_brain *get_brain_pointer() { return &brain; }

double *get_current_cost() { return current_params.cost; }

double *get_current_weights() { return current_params.weight; }

void boot_brain() {
    brain.rng = 1;
    brain.new_piece = 0;
    brain.suicide = 0;
    brain.round_has_cleaned_lines = 0;
    initialize_agent();
}


void _store_piece(char piece) {
#ifdef print_piece_sequence
    printf("%c", piece);
#endif

    register_piece_spawned(piece);
}

void store_piece() {
    static int counter = 0;
    switch (get_cpu_pointer()->mem_controller.memory[0xc203]) {
        case 0x0c:
        case 0x0d:
        case 0x0e:
        case 0x0f: _store_piece('O'); break;

        case 0x04:
        case 0x05:
        case 0x06:
        case 0x07: _store_piece('J'); break;

        case 0x00:
        case 0x01:
        case 0x02:
        case 0x03: _store_piece('L'); break;

        case 0x08:
        case 0x0a:
        case 0x09:
        case 0x0b: _store_piece('I'); break;

        case 0x14:
        case 0x16:
        case 0x15:
        case 0x17: _store_piece('S'); break;

        case 0x10:
        case 0x12:
        case 0x11:
        case 0x13: _store_piece('Z'); break;

        case 0x18:
        case 0x19:
        case 0x1a:
        case 0x1b: _store_piece('T'); break;

        default: fprintf(stderr, "Invalid piece in get_current_piece\n"); abort();
    }

    if ((counter++) % 5 == 0) {
        fflush(NULL);
    }
}

