import json
import sys
from copy import copy
from random import random

import tasks


def main(fast):
    best = {"lines_cleared": 0}
    results = []

    agent_settings = {
        "agent": {"weights": [(random() * 2 - 1) * 5 for _ in range(14 * 3)]}
    }

    if fast:
        print(tasks.run_agent_task(agent_settings))
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


if __name__ == "__main__":
    fast = len(sys.argv) > 1 and sys.argv[1] == "fast"

    main(fast)
