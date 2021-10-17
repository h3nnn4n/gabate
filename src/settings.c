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

#include "settings.h"

_agent_config agent_config;

void load_settings(char *setting_str) {
    const cJSON *object = NULL;
    cJSON *      json   = cJSON_Parse(setting_str);

    if (json == NULL)
        abort();

    agent_config.settings = json;

    cJSON *agent   = cJSON_GetObjectItemCaseSensitive(json, "agent");
    cJSON *weights = cJSON_GetObjectItemCaseSensitive(agent, "weights");

    agent_config.agent_weights = malloc(sizeof(double) * cJSON_GetArraySize(weights));

    unsigned int index = 0;
    cJSON_ArrayForEach(object, weights) {
        agent_config.agent_weights[index] = object->valuedouble;
        index++;
    }
}

double *get_agent_weights() { return agent_config.agent_weights; }
