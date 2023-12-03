import json
import statistics
import dramatiq
from copy import copy
from random import uniform
from uuid import uuid4

import config
import tasks


class Agent:
    def __init__(self):
        self.n_weights = 14 * 3
        self.n_evals = 7
        self.settings = {}
        self.set_random_weights()
        self.id = str(uuid4())

        self.settings["agent_id"] = self.id

        self.pending_results = []

        self._scores = []
        self._dirty_fitness = True

    def set_random_weights(self):
        self._dirty_fitness = True
        self.settings["weights"] = [uniform(-5.0, 5.0) for _ in range(self.n_weights)]

    def set_weights(self, weights):
        assert len(weights) == len(self.settings["weights"])

        if weights == self.settings["weights"]:
            return

        self._dirty_fitness = True
        self.settings["weights"] = copy(self.settings["weights"])

    def get_agent_data(self):
        return {"agent": self.settings}

    def trigger_eval(self, force=False):
        if not force and not self._dirty_fitness:
            return

        data = self.get_agent_data()

        self.pending_results = [tasks.evaluate_agent.send(data) for _ in range(self.n_evals)]

    def _get_scores(self):
        values = []

        for _index, result in enumerate(self.pending_results):
            while True:
                try:
                    value = result.get_result(block=True)
                    values.append(json.loads(value))
                    break
                except dramatiq.results.ResultTimeout:
                    continue

        return [value.get("lines_cleared") for value in values]

    def get_fitness(self):
        if self._dirty_fitness:
            self._dirty_fitness = False
            self._scores = self._get_scores()

        scores = self._scores

        fitness = {
            "min": min(scores),
            "median": statistics.median(scores),
            "max": max(scores),
            "raw": sorted(scores),
        }

        return fitness

    def clone(self):
        new = Agent()
        new.settings["weights"] = copy(self.settings["weights"])
        new._dirty_fitness = self._dirty_fitness
        new._scores = copy(self._scores)
        return new
