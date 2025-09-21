/******************************************************************************
 * Copyright (C) 2021, 2025  Renan S. Silva                                   *
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
#include "utils.h"

_agent_config agent_config;

void load_settings(char *setting_str) {
    const cJSON *object = NULL;
    cJSON       *json   = cJSON_Parse(setting_str);

    if (json == NULL) {
        fprintf(stderr, "Failed to parse agent settings\n");
        abort();
    }

    cJSON *debug_mode = cJSON_GetObjectItem(json, "debug_mode");
    if (debug_mode != NULL) {
        agent_config.debug_mode = cJSON_IsTrue(debug_mode);
    } else {
        printf("defaulting to debug mode\n");
        agent_config.debug_mode = true;
    }

    cJSON *ping = cJSON_GetObjectItemCaseSensitive(json, "ping");
    if (ping != NULL && strcmp(ping->valuestring, "foobar") == 0) {
        agent_config.ping_mode = true;
        printf("ping mode enabled\n");
        return;
    }

    cJSON *capture_output = cJSON_GetObjectItemCaseSensitive(json, "capture_output");
    if (capture_output != NULL) {
        agent_config.capture_output = cJSON_IsTrue(capture_output);
    } else {
        printf_debug("defaulting to not capture output\n");
        agent_config.capture_output = false;
    }

    agent_config.settings = json;

    cJSON *agent = cJSON_GetObjectItemCaseSensitive(json, "agent");
    if (agent == NULL) {
        fprintf(stderr, "\"agent\" key not found. Can't run an agent without it\n");
        abort();
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

        printf_debug("loaded %d weights\n", index);
    } else {
        fprintf(stderr, "\"weights\" key not found. Can't run an agent without it\n");
        abort();
    }

    cJSON *run_id = cJSON_GetObjectItem(agent, "run_id");
    if (run_id != NULL) {
        agent_config.run_id = (char *)malloc(sizeof(char) * (strlen(run_id->valuestring) + 1));
        snprintf(agent_config.run_id, strlen(run_id->valuestring) + 1, "%s", run_id->valuestring);
    } else {
        printf_debug("run id not set. Using dummy.\n");
        agent_config.run_id = (char *)malloc(sizeof(char) * 4);
        strcpy(agent_config.run_id, "foo");
    }

    cJSON *agent_id = cJSON_GetObjectItem(agent, "agent_id");
    if (agent_id != NULL) {
        agent_config.agent_id = (char *)malloc(sizeof(char) * (strlen(agent_id->valuestring) + 1));
        snprintf(agent_config.agent_id, strlen(agent_id->valuestring) + 1, "%s", agent_id->valuestring);
    } else {
        printf_debug("agent id not set. Using dummy.\n");
        agent_config.agent_id = (char *)malloc(sizeof(char) * 4);
        strcpy(agent_config.agent_id, "bar");
    }

    cJSON *feature_set_name = cJSON_GetObjectItem(agent, "feature_set_name");
    if (feature_set_name != NULL) {
        agent_config.feature_set_name = (char *)malloc(sizeof(char) * (strlen(feature_set_name->valuestring) + 1));
        snprintf(agent_config.feature_set_name, strlen(feature_set_name->valuestring) + 1, "%s",
                 feature_set_name->valuestring);
    } else {
        fprintf(stderr, "fature set not set. Aborting.\n");
        abort();
    }
}

double *get_agent_weights() {
    if (agent_config.ping_mode && agent_config.agent_weights == NULL) {
        // HACK: This should be enough for the forseable future
        agent_config.agent_weights = (double *)malloc(sizeof(double) * 1000);
    }

    assert(agent_config.agent_weights != NULL);

    return agent_config.agent_weights;
}

_agent_config *get_agent_config() { return &agent_config; }

bool pong() {
    if (!agent_config.ping_mode)
        return false;

    printf("{\"pong\": \"foo bar\"}");
    return true;
}

bool is_debug_mode() { return agent_config.debug_mode; }