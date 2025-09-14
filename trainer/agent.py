import json
import logging
import statistics
import time
import typing as t
from collections import defaultdict
from copy import copy
from random import uniform
from uuid import uuid4

import config
import tasks
from queueer.task import TaskNotFinishedError, send_task

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        self.n_weights = 14 * 3
        self.n_evals = config.N_AGENT_EVALS  # type: ignore
        self.settings = {}
        self.set_random_weights()
        self.id = str(uuid4())

        self.settings["agent_id"] = self.id
        self.settings["feature_set_name"] = config.FEATURE_SET_NAME  # type: ignore

        self.pending_results = []

        self._scores = []
        self._dirty_fitness = True

        logger.info(f"created {self.id=}")

    def set_random_weights(self):
        self._dirty_fitness = True
        self.settings["weights"] = [uniform(-5.0, 5.0) for _ in range(self.n_weights)]

    def set_weights(self, weights):
        assert len(weights) == len(self.settings["weights"])

        if weights == self.settings["weights"]:
            return

        self._dirty_fitness = True
        self.settings["weights"] = copy(weights)

    def set_weight(self, index, value):
        assert 0 <= index < self.n_weights

        if self.settings["weights"][index] == value:
            return

        self._dirty_fitness = True
        self.settings["weights"][index] = value

    def get_agent_data(self):
        return {"agent": self.settings}

    def trigger_eval(self, force=False):
        if not force and not self._dirty_fitness:
            return

        logger.info(f"triggering eval for {self.id=}")

        data = self.get_agent_data()

        self.pending_results = []
        for _index in range(self.n_evals):
            key = f"{self.id}:{_index}"
            self.pending_results.append(
                send_task(
                    task=tasks.evaluate_agent_task,
                    task_id=key,
                    args=[data],
                )
            )

        self._dirty_fitness = True

    def _get_scores(self):
        values = []

        logger.info(f"getting scores for {self.id=} {self._dirty_fitness}")

        results_by_index = defaultdict(lambda: False)

        while True:
            for _index, result in enumerate(self.pending_results):
                if results_by_index[_index]:
                    continue

                try:
                    agent_raw_result = result.get_result()

                    if agent_raw_result is None:
                        raise Exception("Agent result is None")

                    agent_result = json.loads(agent_raw_result)
                    values.append(agent_result)
                    lines_cleared = agent_result.get("lines_cleared")
                    pieces_spawned = agent_result.get("pieces_spawned")
                    logger.info(f"got {_index} result from {self.id=} {lines_cleared=} {pieces_spawned=}")

                    print(f"got {_index} result from {self.id=} with {lines_cleared=} {pieces_spawned=}")
                    results_by_index[_index] = True
                    break
                except TaskNotFinishedError:
                    pass
                except json.JSONDecodeError:
                    raise Exception("Agent result is not valid JSON")
                except Exception as e:
                    raise Exception(f"Got exception while awaiting agent result: {e}")

            if all(results_by_index.values()):
                break

            time.sleep(0.2)

        scores = [agent_result.get("lines_cleared") for agent_result in values]
        print(f"got {len(scores)} scores for {self.id=}")
        return scores

    def get_fitness(self):
        if self._dirty_fitness:
            self._scores = self._get_scores()
            self._dirty_fitness = False

            if not self._scores:
                raise ValueError("agent hasn't been evaluated yet")

        scores = self._scores

        fitness = {
            "min": min(scores),
            "median": statistics.median(scores),
            "avg": sum(scores) / len(scores),
            "max": max(scores),
            "sum": sum(scores),
            "raw": sorted(scores),
        }

        return fitness

    def clone(self):
        new = Agent()
        new.settings["weights"] = copy(self.settings["weights"])
        new.settings["feature_set_name"] = self.settings["feature_set_name"]
        new._dirty_fitness = self._dirty_fitness
        new._scores = copy(self._scores)
        new.pending_results = copy(self.pending_results)
        logger.info(f"cloning {self.id=} to {new.id=}")
        return new


class Individual:
    def __init__(self, agent=None):
        self._agent = agent or Agent()
        self.id = self._agent.id
        self.n_genes = 14 * 3
        self.genes = [uniform(-5, 5) for _ in range(self.n_genes)]

    def set_genes(self, genes: list[float]):
        assert len(genes) == self.n_genes

        if genes == self.genes:
            return

        self._dirty_fitness = True
        self.genes = genes
        self._agent.set_weights(genes)

    def evaluate_fitness(self, force: bool = False) -> None:
        self._agent.set_weights(self.genes)
        self._agent.trigger_eval(force)
        self._agent.get_fitness()

    def trigger_fitness_evaluation(self, force: bool = False) -> None:
        self._agent.trigger_eval(force)

    def get_fitness(self):
        result = self._agent.get_fitness()

        # Short circuit fitness to zero if IA fails to score anything during any evals
        if result["min"] == 0:
            return 0

        match config.FITNESS_MODE.upper():  # type: ignore
            case "MAX":
                return result["max"]
            case "MIN":
                return result["min"]
            case "MEDIAN":
                return result["median"]
            case "SUM":
                return result["sum"]
            case "AVG":
                return result["avg"]
            case _:
                raise ValueError(f"{config.FITNESS_MODE} is not a valid option")  # type: ignore

    def get_raw_fitness(self) -> dict[str, float]:
        return self._agent.get_fitness()

    def clone(self):
        copy_agent = self._agent.clone()
        new = Individual(agent=copy_agent)
        new.n_genes = self.n_genes
        new.genes = copy(self.genes)

        return new

    @property
    def settings(self) -> dict[str, t.Any]:
        return self._agent.settings
