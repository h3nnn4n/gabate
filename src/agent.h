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

#ifndef SRC_AGENT_H_
#define SRC_AGENT_H_

#include "lelmark.h"
#include "trainer.h"
#include "types.h"

extern _best_piece best_piece;
extern _move_queue move_queue;
extern _ai_state   ai_state;

_best_piece *get_best_piece_pointer();

void       set_cpu_pointer(_cpu_info *cpu);
_cpu_info *get_cpu_pointer();

void logic_update();

int  piece_moved();
void start_game_hook();
void joystick_hook();

#endif  // SRC_AGENT_H_
