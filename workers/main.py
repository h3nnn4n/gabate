import sys
from random import random

import tasks


def main(fast):
    results = []
    agent_settings = {
        "agent": {"weights": [(random() * 2 - 1) * 5 for _ in range(14 * 3)]}
    }

    if fast:
        print(tasks.run_agent_task(agent_settings))
        return

    for i in range(5):
        agent_settings["agent"]["weights"] = [
            (random() * 2 - 1) * 5 for _ in range(14 * 3)
        ]
        results.append(tasks.a_plus_b.delay(i, i + 1))
        results.append(tasks.run_agent_task.delay(agent_settings))

    for result in results:
        print(result.get())


if __name__ == "__main__":
    fast = len(sys.argv) > 1 and sys.argv[1] == "fast"

    main(fast)
