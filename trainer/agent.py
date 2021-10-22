import json
import statistics
from random import randrange

from .tasks import evaluate_agent


class Agent:
    def __init__(self):
        self.n_weights = 14 * 3
        self.n_evals = 7
        self.settings = {}
        self.set_random_weights()

        self.pending_results = []

    def set_random_weights(self):
        self.settings["weights"] = [randrange(-5, 5) for _ in range(self.n_weights)]

    def to_json(self):
        data = {"agent": self.settings}

        return json.dumps(data)

    def trigger_eval(self):
        data = self.to_json()

        self.pending_results = [
            evaluate_agent.delay(data) for _ in range(self.n_evals)
        ]

    def get_fitness(self):
        values = [result.get() for result in self.pending_results]
        return statistics.median(values)
