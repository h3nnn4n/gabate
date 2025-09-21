import json
import os
from pprint import pprint
from uuid import uuid4

from tqdm import tqdm

import config
from agent import Individual, load_agent
from logging_config import get_logger

logger = get_logger(__name__)

GRID_SEARCH_RANGE = config.GENE_RANGE  # type: ignore
GRID_SEARCH_STEP = config.GENE_STEP_SIZE  # type: ignore

RUN_ID = str(uuid4())[:8]


def grid_searcher(individual_path: str):
    individual = load_agent(individual_path, evaluate=True)

    run_grid_search(individual)


def run_grid_search(individual: Individual):
    test_individuals = []
    best_score = 0

    for i in range(individual.n_genes):
        elite_individual = individual.clone()

        logger.info("")
        logger.info(
            f"running grid search for gene {i + 1}/{individual.n_genes}"
        )

        test_individuals = []
        grid_range = GRID_SEARCH_RANGE * 2
        n_grid_steps = int(grid_range // GRID_SEARCH_STEP) + 1  # Rather search a bit more than a bit less

        for j in range(n_grid_steps):
            gene_value = j * GRID_SEARCH_STEP - GRID_SEARCH_RANGE
            new_genes = individual.genes.copy()
            new_genes[i] = gene_value
            test_individual = Individual()
            test_individual.set_genes(new_genes)
            test_individuals.append(test_individual)

        for test_individual in test_individuals:
            test_individual.trigger_fitness_evaluation()

        scores = [test_individual.get_fitness() for test_individual in tqdm(test_individuals, desc="evaluating")]

        for test_individual, score in zip(test_individuals, scores):
            if score > best_score:
                best_score = score
                elite_individual = test_individual.clone()
                elite_individual.set_genes(test_individual.genes)
                logger.info(f"new best individual {score=}")

        logger.info(f"iteration {i} best score:")
        logger.info(f"{elite_individual.get_raw_fitness()}")

        individual.set_genes(elite_individual.genes)

        store_elite(elite_individual, i, elite_individual.get_fitness())


def store_elite(individual: Individual, generation_count: int, elite_score: float):
    base_path = "results/grid_searcher/"
    os.makedirs(base_path, exist_ok=True)

    with open(f"{base_path}/elite_individual__{RUN_ID}__{generation_count}_score_{elite_score}.json", "wt") as f:
        f.write(json.dumps(individual.settings, indent=2))
