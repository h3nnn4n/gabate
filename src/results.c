/******************************************************************************
 * Copyright (C) 2021  Renan S. Silva                                         *
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

#include "results.h"

_agent_results agent_results;

void set_lines_cleared(int lines_cleared) {
    if (agent_results.results == NULL)
        agent_results.results = cJSON_CreateObject();

    cJSON_AddNumberToObject(agent_results.results, "lines_cleared", lines_cleared);
}

void set_pieces_spawned(int pieces_spawned) {
    if (agent_results.results == NULL)
        agent_results.results = cJSON_CreateObject();

    cJSON_AddNumberToObject(agent_results.results, "pieces_spawned", pieces_spawned);
}

void register_piece_spawned(char piece) {
    if (agent_results.results == NULL)
        agent_results.results = cJSON_CreateObject();

    cJSON *pieces = NULL;

    pieces = cJSON_GetObjectItem(agent_results.results, "pieces");
    if (pieces == NULL)
        pieces = cJSON_AddArrayToObject(agent_results.results, "pieces");

    char piece_str[16];
    snprintf(piece_str, 16, "%c", piece);
    cJSON *piece_json = cJSON_CreateString(piece_str);
    cJSON_AddItemToArray(pieces, piece_json);
}

void print_agent_results() {
    if (agent_results.results == NULL)
        return;

    char *string = cJSON_Print(agent_results.results);
    printf("%s\n", string);
}
