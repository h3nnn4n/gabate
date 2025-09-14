import json
import platform
from subprocess import PIPE, Popen

from queueer.task import Task


def evaluate_agent(agent_settings):
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
    except Exception as e:
        print(f"finished running {agent_id=} with exception: {e}")

    return result


evaluate_agent_task = Task(
    name="evaluate_agent",
    callable=evaluate_agent,
)

# TODO: Should be dynamic
TASK_REGISTRY = {
    "evaluate_agent": evaluate_agent_task,
}


def get_task_by_name(name: str) -> Task:
    if name not in TASK_REGISTRY:
        raise ValueError(f"Unknown task name: {name}")
    return TASK_REGISTRY[name]
