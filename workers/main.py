import json
from copy import copy
from random import random

from . import tasks
from .agent import Agent


def main(fast):
    best = {"lines_cleared": 0}
    results = []

    if fast:
        agent = Agent()
        agent.trigger_eval()
        print(agent.get_fitness())
        return

    for i in range(50):
        agent_settings["agent"]["weights"] = [
            (random() * 2 - 1) * 5 for _ in range(14 * 3)
        ]
        results.append(tasks.run_agent_task.delay(agent_settings))

    for index, result in enumerate(results):
        data = json.loads(result.get())
        if data["lines_cleared"] > best["lines_cleared"]:
            best = copy(data)
            print(f'{index:4} {best["lines_cleared"]:4}')
