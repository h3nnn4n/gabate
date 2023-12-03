import json
import platform
from subprocess import PIPE, Popen

import config


def run_agent(agent_settings):
    env = {}
    payload = json.dumps(agent_settings)
    args = ["../gabate", "../roms/tetris.gb", payload]

    if platform.system() == "Linux":
        env["LD_LIBRARY_PATH"] = "../deps/cJSON/build/"

    with Popen(args, stdout=PIPE, env=env) as proc:
        output_stdout = proc.stdout.read()

    return output_stdout.decode()
