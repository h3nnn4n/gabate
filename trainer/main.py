from agent import Agent
from utils import get_n_workers
from worker import worker


def main():
    # Basic sanity check
    x = worker.send_task("tasks.a_plus_b", args=[1, 2])
    assert x.get() == 3

    n_nodes, n_workers = get_n_workers()
    print(f"running with {n_nodes} nodes and {n_workers} workers")

    agents = [Agent() for _ in range(50)]

    for agent in agents:
        agent.trigger_eval()

    agents = sorted(agents, key=lambda x: x.get_fitness()[0], reverse=True)
    print(agents[0].get_fitness())
    agents = sorted(agents, key=lambda x: x.get_fitness()[1], reverse=True)
    print(agents[0].get_fitness())
    agents = sorted(agents, key=lambda x: x.get_fitness()[2], reverse=True)
    print(agents[0].get_fitness())

    agents = [x for x in agents if x.get_fitness()[0] > 0]

    agents = sorted(agents, key=lambda x: x.get_fitness()[1], reverse=True)
    print(agents[0].get_fitness())
    agents = sorted(agents, key=lambda x: x.get_fitness()[2], reverse=True)
    print(agents[0].get_fitness())


if __name__ == "__main__":
    main()
