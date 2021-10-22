import json
from subprocess import PIPE, Popen


def run_agent(agent_settings):
    payload = json.dumps(agent_settings)
    args = ["../gabate", "../roms/tetris.gb", payload]

    with Popen(args, stdout=PIPE) as proc:
        output_stdout = proc.stdout.read()

    return output_stdout.decode()