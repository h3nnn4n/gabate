from agent import Agent
from worker import worker


def main():
    x = worker.send_task("tasks.a_plus_b", args=[1, 2])
    assert x.get() == 3

    agent = Agent()
    agent.trigger_eval()
    # print(agent.get_fitness())


if __name__ == "__main__":
    main()
