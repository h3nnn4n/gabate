import json
import platform
from subprocess import PIPE, Popen

import config  # noqa


def run_agent(agent_settings):
    payload = json.dumps(agent_settings)
    agent_id = agent_settings["agent"]["agent_id"]

    print(f"running {agent_id=}")
    env = {}
    args = ["../gabate", "../roms/tetris.gb", payload]

    if platform.system() == "Linux":
        env["LD_LIBRARY_PATH"] = "../deps/cJSON/build/"

    with Popen(args, stdout=PIPE, env=env) as proc:
        output_stdout = proc.stdout.read()

    result = output_stdout.decode()
    try:
        result_data = json.loads(result)
        lines_cleared = result_data["lines_cleared"]
        pieces_spawned = result_data["pieces_spawned"]

        print(f"finished running {agent_id=} {pieces_spawned=:4d}     {lines_cleared=:4d}")
    except json.decoder.JSONDecodeError:
        print(f"finished running {agent_id=}")

    return result
