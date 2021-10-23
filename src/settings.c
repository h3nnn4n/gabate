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

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <cJSON.h>

#include "settings.h"

_agent_config agent_config;

void load_settings(char *setting_str) {
    const cJSON *object = NULL;
    cJSON *      json   = cJSON_Parse(setting_str);

    if (json == NULL) {
        fprintf(stderr, "Failed to parse agent settings\n");
        abort();
    }

    agent_config.settings = json;

    cJSON *agent = cJSON_GetObjectItemCaseSensitive(json, "agent");
    if (agent == NULL) {
        fprintf(stderr, "\"agent\" key not found. Can't run an agent without it\n");
    }

    cJSON *weights = cJSON_GetObjectItemCaseSensitive(agent, "weights");

    if (weights != NULL) {
        agent_config.agent_weights = (double *)malloc(sizeof(double) * cJSON_GetArraySize(weights));
        assert(agent_config.agent_weights);

        unsigned int index = 0;
        cJSON_ArrayForEach(object, weights) {
            agent_config.agent_weights[index] = object->valuedouble;
            index++;
        }
    } else {
        fprintf(stderr, "\"weights\" key not found. Can't run an agent without it\n");
    }

    cJSON *train = cJSON_GetObjectItem(json, "train");
    if (train != NULL) {
        agent_config.train = cJSON_IsTrue(train);
    }

    cJSON *run_id = cJSON_GetObjectItem(agent, "run_id");
    if (run_id != NULL) {
        agent_config.run_id = (char *)malloc(sizeof(char) * (strlen(run_id->valuestring) + 2));
        snprintf(agent_config.run_id, strlen(agent_config.run_id), "%s", run_id->valuestring);
    }

    cJSON *agent_id = cJSON_GetObjectItem(agent, "agent_id");
    if (agent_id != NULL) {
        agent_config.agent_id = (char *)malloc(sizeof(char) * (strlen(agent_id->valuestring) + 2));
        snprintf(agent_config.agent_id, strlen(agent_config.agent_id), "%s", agent_id->valuestring);
    }
}

double *get_agent_weights() {
    assert(agent_config.agent_weights != NULL);

    return agent_config.agent_weights;
}

bool get_train() { return agent_config.train; }

_agent_config *get_agent_config() { return &agent_config; }
