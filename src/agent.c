/******************************************************************************
 * Copyright (C) 2016-2017,2021  Renan S. Silva                               *
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

#include <stdio.h>
#include <stdlib.h>

#include <cJSON.h>

#include "agent.h"
#include "file_control.h"
#include "stats.h"
#include "utils_dev.h"

// TODO: This should be a setting
#define fast_training 1

_best_piece best_piece;
_move_queue move_queue;
_ai_state   ai_state;
_cpu_info * cpu_info;  // This probably doesnt belong here

// Why in the seven heavens have I done this?
void       set_cpu_pointer(_cpu_info *cpu) { cpu_info = cpu; }
_cpu_info *get_cpu_pointer() { return cpu_info; }

_best_piece *get_best_piece_pointer() { return &best_piece; }

void rotation_changed_hook() {
    static int rotation = -1;  // get_cpu_pointer()->mem_controller.memory[0xc203];

    if (rotation != get_cpu_pointer()->mem_controller.memory[0xc203]) {
        if (piece_moved()) {
            move_queue.wait_rotation = 0;
            /*printf("rotation hook\n");*/
            best_piece.nrotations--;
        }
    }

    rotation = get_cpu_pointer()->mem_controller.memory[0xc203];
}

void joystick_hook() {
    int x = get_cpu_pointer()->mem_controller.memory[0xff92] - 8;
    /*int y = get_cpu_pointer()->mem_controller.memory[0xff93] - 16;*/
    _cpu_info *cpu = get_cpu_pointer();

    /*rotation_changed_hook();*/

    /*printf("Joystick hook\n");*/

    start_game_hook();

    if (cpu->pc == 0x2a0e) {
        switch (ai_state.game_state) {
            case INGAME:
                switch (move_queue.ready) {
                    case 0:
                        cpu->joystick.button_start  = 1;
                        cpu->joystick.button_select = 1;
                        cpu->joystick.button_b      = 1;
                        cpu->joystick.button_a      = 1;
                        cpu->joystick.button_down   = 1;
                        cpu->joystick.button_up     = 1;
                        cpu->joystick.button_left   = 1;
                        cpu->joystick.button_right  = 1;

                        move_queue.ready = 1;
                        break;
                    case 1:
                        move_queue.ready = 0;

                        if (get_brain_pointer()->suicide && fast_training) {
                            cpu->joystick.button_down = 0;
                            break;
                        }

                        if (best_piece.nrotations > 0 /*&& move_queue.wait_rotation == 0*/) {
                            /*printf("Called rotation %2d\n", best_piece.nrotations);*/
                            cpu->joystick.button_b   = 0;
                            move_queue.wait_rotation = 1;
                            best_piece.nrotations--;
                        }

                        // FIXME Check out the best move strategy

                        if (best_piece.coord.x > x) {
                            cpu->joystick.button_right = 0;
                        } else if (best_piece.coord.x < x) {
                            cpu->joystick.button_left = 0;
                        }

                        if (best_piece.coord.x == x) {
                            cpu->joystick.button_down = 0;
                        }
                        break;
                    case 2: break;
                    default: fprintf(stderr, "Invalid ready status at joystick_hook\n"); abort();
                }
                break;
            case BOOTING:
            case GAMEOVER:
                /*printf("BOOT/GAMEOVER button\n");*/
                switch (move_queue.ready) {
                    case 0:
                        cpu->joystick.button_start  = 1;
                        cpu->joystick.button_select = 1;
                        cpu->joystick.button_b      = 1;
                        cpu->joystick.button_a      = 1;
                        cpu->joystick.button_down   = 1;
                        cpu->joystick.button_up     = 1;
                        cpu->joystick.button_left   = 1;
                        cpu->joystick.button_right  = 1;

                        move_queue.ready = 1;
                        break;
                    case 1:
                        if (get_brain_pointer()->rng && drand48() < .25) {
                            move_queue.ready = 0;

                            cpu->joystick.button_start = 0;
                            break;
                        } else if (get_brain_pointer()->rng == 0) {
                            move_queue.ready = 0;

                            cpu->joystick.button_start = 0;
                            break;
                        }
                    case 2: break;
                    default: fprintf(stderr, "Invalid ready status at joystick_hook\n"); abort();
                }
                break;
            default: break;
        }
    }
}

int piece_moved() {
    static int x = -1;
    static int y = -1;

    int ret = 0;

    int x2 = get_cpu_pointer()->mem_controller.memory[0xff92] - 8;
    int y2 = get_cpu_pointer()->mem_controller.memory[0xff93] - 16;

    if (x != x2 || y != y2) {
        /*printf("Piece moved\n");*/
        ret = 1;
    }

    x = x2;
    y = y2;

    return ret;
}

void mem_fiddling() {
    if (cpu_info->mem_controller.memory[0xffe1] == 0x0000) {
        char text[256];
        int  index;
        int  pos = 140;

        sprintf(text, "0xff80 = %04x " BYTE_TO_BINARY_PATTERN, cpu_info->mem_controller.memory[0xff80],
                BYTE_TO_BINARY(cpu_info->mem_controller.memory[0xff80]));
        draw_text(text, 400, 20, 0x2a, 0x90, 0xf5);

        sprintf(text, "0xff81 = %04x " BYTE_TO_BINARY_PATTERN, cpu_info->mem_controller.memory[0xff81],
                BYTE_TO_BINARY(cpu_info->mem_controller.memory[0xff81]));
        draw_text(text, 400, 40, 0x2a, 0x90, 0xf5);

        index = 0xff93;
        sprintf(text, "y: 0x%04x = %02d ", index, cpu_info->mem_controller.memory[index]);
        draw_text(text, 400, 60, 0x2a, 0x90, 0xf5);

        index = 0xff92;
        sprintf(text, "x: 0x%04x = %02d ", index, cpu_info->mem_controller.memory[index]);
        draw_text(text, 400, 80, 0x2a, 0x90, 0xf5);

        ////////////////////

        sprintf(text, "Most Cleared: %5d", get_brain_pointer()->most_lines_cleared);
        draw_text(text, 400, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        sprintf(text, "Worst Cleared: %4d", get_brain_pointer()->worst_lines_cleared);
        draw_text(text, 400, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        /*sprintf(text, "best: %3d , %3d ", best_piece.coord.x, best_piece.coord.y);*/
        /*draw_text(text, 40, pos, 0x2a, 0x90, 0xf5);*/
        /*pos += 20;*/

        _brain *brain = get_brain_pointer();

        sprintf(text, "Lines Cleared: %4d", brain->population[brain->current].fitness);
        draw_text(text, 400, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        sprintf(text, "Least Cleared: %4d", get_brain_pointer()->population[get_brain_pointer()->current].worst);
        draw_text(text, 400, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        index = 0x994e;
        sprintf(text, "0x%04x = %02d %02x ", index, cpu_info->mem_controller.memory[index],
                cpu_info->mem_controller.memory[index]);
        draw_text(text, 400, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        index = 0x994f;
        sprintf(text, "0x%04x = %02d %02x ", index, cpu_info->mem_controller.memory[index],
                cpu_info->mem_controller.memory[index]);
        draw_text(text, 400, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        index = 0x9950;
        sprintf(text, "0x%04x = %02d %02x ", index, cpu_info->mem_controller.memory[index],
                cpu_info->mem_controller.memory[index]);
        draw_text(text, 400, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        index = 0x9951;
        sprintf(text, "0x%04x = %02d %02x ", index, cpu_info->mem_controller.memory[index],
                cpu_info->mem_controller.memory[index]);
        draw_text(text, 400, pos, 0x2a, 0x90, 0xf5);

        ////////////////////
        /*sprintf(text, "best: %3d , %3d ", best_piece.coord.x, best_piece.coord.y);*/
        /*draw_text(text, 20, pos, 0xff, 0x00, 0x00);*/
        ////////////////////

        pos = 0;

        sprintf(text, "diversity:   %f", get_brain_pointer()->diversity);
        draw_text(text, 110, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        sprintf(text, "generations: %3d", get_brain_pointer()->elapsed_generations);
        draw_text(text, 110, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        sprintf(text, "current:     %3d/%d", get_brain_pointer()->current, POP_SIZE);
        draw_text(text, 110, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        sprintf(text, "runs:        %3d/%d", get_brain_pointer()->runs, get_brain_pointer()->max_runs);
        draw_text(text, 110, pos, 0x2a, 0x90, 0xf5);
        pos += 20;

        ////////////////////
    }
}

void new_piece_on_screen_hook() {
    static int old_pos = 100;
    _cpu_info *cpu     = get_cpu_pointer();

    _brain *brain = get_brain_pointer();

    /*uint16_t y_pos = 0xffb2;*/
    uint16_t y_pos = 0xff93;

    piece_moved();

    /*int x = get_cpu_pointer()->mem_controller.memory[0xff92] - 8;*/
    /*int y = get_cpu_pointer()->mem_controller.memory[0xff93] - 16;*/

    if (brain->new_piece) {
        update_stats(cpu->mem_controller.memory[0xc203]);

        /*if ( brain->population[brain->current].fitness > brain->population[brain->current].worst && brain->runs > 0 )
         * {*/
        /*brain->suicide = 1;*/
        /*}*/

        print_piece();

        brain->new_piece = 0;
        /*evaluate_cost();*/

        brain->population[brain->current].pieces_spawned_total++;
        brain->population[brain->current].pieces_spawned[brain->runs]++;

        update_fitness();
        get_best_move();
        /*best = get_best_move();*/
        /*printf("%3d %3d\n", x, y);*/
        screen_update();
    } else if (old_pos < cpu->mem_controller.memory[y_pos]) {
        /*printf("%3d %3d %3d %3d\n", x, y, old_pos, cpu->mem_controller.memory[y_pos]);*/
    }

    old_pos = cpu->mem_controller.memory[y_pos];
}

void game_over_hook() {
    static int old   = -1;
    int        atual = cpu_info->mem_controller.memory[0xffe1];

    if (atual == 0x000d && old != atual) {
        get_brain_pointer()->suicide = 0;
        reset_bg();
        check_stop_condition();
        update_fitness();
        ai_state.game_state = GAMEOVER;
        finished_evaluating_individual();
        reset_file_control();
    }

    old = atual;
}
void start_game_hook() {
    static int old   = -1;
    int        atual = cpu_info->mem_controller.memory[0xffe1];

    if (atual == 0x0000 && old != atual) {
        get_best_move();
        get_brain_pointer()->rng = 0;
        move_queue.ready         = 0;
        ai_state.game_state      = INGAME;
        set_can_write_file_control();
    }

    old = atual;
}

void logic_update() {
    start_game_hook();
    game_over_hook();

    if (cpu_info->mem_controller.memory[0xffe1] == 0x0000) {
        new_piece_on_screen_hook();
    }
}
