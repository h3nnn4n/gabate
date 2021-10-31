import json
import statistics
from copy import copy
from random import uniform
from uuid import uuid4

from worker import worker


class Agent:
    def __init__(self):
        self.n_weights = 14 * 3
        self.n_evals = 7
        self.settings = {}
        self.set_random_weights()
        self.id = uuid4()

        self.settings["agent_id"] = self.id

        self.pending_results = []

        self._scores = []
        self._dirty_fitness = True

    def set_random_weights(self):
        self._dirty_fitness = True
        self.settings["weights"] = [uniform(-5.0, 5.0) for _ in range(self.n_weights)]

    def set_weights(self, weights):
        self._dirty_fitness = True
        assert len(weights) == len(self.settings["weights"])
        self.settings["weights"] = copy(self.settings["weights"])

    def get_agent_data(self):
        return {"agent": self.settings}

    def trigger_eval(self, force=False):
        if not force and not self._dirty_fitness:
            return

        data = self.get_agent_data()

        self.pending_results = [worker.send_task("tasks.evaluate_agent", args=[data]) for _ in range(self.n_evals)]

    def _get_scores(self):
        values = [json.loads(result.get()) for result in self.pending_results]
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
