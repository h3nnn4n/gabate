import json
import statistics
from random import randrange

from worker import worker


class Agent:
    def __init__(self):
        self.n_weights = 14 * 3
        self.n_evals = 7
        self.settings = {}
        self.set_random_weights()

        self.pending_results = []

    def set_random_weights(self):
        self.settings["weights"] = [randrange(-5, 5) for _ in range(self.n_weights)]

    def get_agent_data(self):
        return{"agent": self.settings}

    def trigger_eval(self):
        data = self.get_agent_data()

        self.pending_results = [
            worker.send_task("tasks.evaluate_agent", args=[data])
            for _ in range(self.n_evals)
        ]

    def get_fitness(self):
        values = [result.get() for result in self.pending_results]
        return statistics.median(values)
