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
from queueer.task import TaskFailedError, TaskNotFinishedError, send_task

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        self.n_weights = config.N_GENES  # type: ignore
        self.n_evals = config.N_AGENT_EVALS  # type: ignore
        self.settings = {}
        self.set_random_weights()
        self.id = str(uuid4())

        self.settings["agent_id"] = self.id
        self.settings["feature_set_name"] = config.FEATURE_SET_NAME  # type: ignore

        self.pending_results = []

        self._scores = []
        self._dirty_fitness = True

        logger.debug(f"created {self.id=}")

    def set_random_weights(self):
        self._dirty_fitness = True
        self.settings["weights"] = [uniform(-config.GENE_RANGE, config.GENE_RANGE) for _ in range(self.n_weights)]  # type: ignore

    def set_weights(self, weights):
        assert len(weights) == len(
            self.settings["weights"]
        ), f"new={len(weights)} current={len(self.settings['weights'])}"

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
        return {
            "debug_mode": False,
            "agent": self.settings,
        }

    def trigger_eval(self, force=False):
        if not force and not self._dirty_fitness:
            return

        logger.debug(f"triggering eval for {self.id=}")

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

    def _get_scores(self, block: bool = True) -> t.Optional[list[float]]:
        values = []

        logger.debug(f"getting scores for {self.id=} {self._dirty_fitness}")

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
                    logger.debug(f"got {_index} result from {self.id=} {lines_cleared=} {pieces_spawned=}")

                    results_by_index[_index] = True
                except TaskNotFinishedError:
                    pass
                except TaskFailedError:
                    raise Exception("Agent result is failed")
                except json.JSONDecodeError:
                    raise Exception("Agent result is not valid JSON")
                except Exception as e:
                    raise Exception(f"Got exception while awaiting agent result: {e}")

            if len(values) == self.n_evals:
                break

            if not block and (len(values) < self.n_evals):
                logger.debug(f"not blocking, returning None found {len(values)} of {self.n_evals} results")
                return None

        assert all(results_by_index.values()), f"Not all results were received: {results_by_index}"
        assert len(values) == len(
            self.pending_results
        ), f"Not all results were received: {len(values)} != {len(self.pending_results)}"
        assert len(values) == self.n_evals, f"Not all results were received: {len(values)} != {self.n_evals}"

        scores = [agent_result.get("lines_cleared") for agent_result in values]
        logger.debug(f"got {len(scores)} scores for {self.id=}")
        return scores

    def get_fitness(self, block: bool = True) -> t.Optional[dict[str, float]]:
        if self._dirty_fitness:
            maybe_scores = self._get_scores(block)

            if not block and maybe_scores is None:
                return None

            self._scores = maybe_scores
            self._dirty_fitness = False

            if not self._scores:
                raise ValueError("agent hasn't been evaluated yet")

        assert self._scores is not None, "scores are not set"
        assert len(self._scores) == self.n_evals, f"Not all results were received: {len(self._scores)} != {self.n_evals}"

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
        new.pending_results = []
        logger.debug(f"cloning {self.id=} to {new.id=}")
        return new


class Individual:
    def __init__(self, agent=None):
        self._agent = agent or Agent()
        self.id = self._agent.id
        self.n_genes = config.N_GENES  # type: ignore
        self.genes = [uniform(-config.GENE_RANGE, config.GENE_RANGE) for _ in range(self.n_genes)]  # type: ignore

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

    def get_fitness(self) -> float:
        result = self._agent.get_fitness(block=True)

        assert result is not None, "get_fitness returned None"

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
        result = self._agent.get_fitness(block=True)
        assert result is not None, "get_raw_fitness returned None"
        return result
    
    @property
    def is_evaluation_ready(self) -> bool:
        result = self._agent.get_fitness(block=False)
        return result is not None

    def clone(self):
        copy_agent = self._agent.clone()
        new = Individual(agent=copy_agent)
        new.n_genes = self.n_genes
        new.genes = copy(self.genes)
        new._dirty_fitness = self._dirty_fitness

        return new

    @property
    def settings(self) -> dict[str, t.Any]:
        return self._agent.settings


def load_agent(individual_path: str, evaluate: bool = False) -> Individual:
    with open(individual_path, "r") as f:
        agent_settings = json.load(f)

    genes = agent_settings["weights"]

    individual = Individual()
    individual.set_genes(genes)

    if evaluate:
        individual.get_fitness()

    return individual