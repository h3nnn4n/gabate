import json
import logging
import os
import random
import signal
import sys
from datetime import datetime, timedelta
from time import sleep
from uuid import uuid4

import config
from agent import Individual, load_agent

logger = logging.getLogger(__name__)

STEP_SIZE = config.GENE_STEP_SIZE  # type: ignore
DURATION = timedelta(minutes=5)

UPDATE_INTERVAL = timedelta(seconds=30)
RUN_ID = str(uuid4())[:8]

should_stop = False


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully by setting the stop flag."""
    global should_stop
    logger.info("Received interrupt signal (Ctrl+C). Stopping search gracefully...")
    should_stop = True


def local_search(individual_path: str):
    global should_stop
    should_stop = False

    signal.signal(signal.SIGINT, signal_handler)

    individual_name = individual_path.split("/")[-1]
    logger.info(f"Starting local search for {individual_name=}")

    elite_individual = load_agent(individual_path, evaluate=False)
    elite_individual.trigger_fitness_evaluation()

    logger.info("Evaluating elite individual")

    population = [elite_individual.clone() for _ in range(config.POPULATION_SIZE)]  # type: ignore
    for individual in population:
        mutate_individual(individual)
        individual.trigger_fitness_evaluation()

    logger.info(f"Evaluating initial population prior to main loop")
    logger.info(f"Elite individual: {json.dumps(elite_individual.get_raw_fitness())}")
    logger.info("Starting main loop")

    original_individual = elite_individual.clone()

    evaluations = 0
    t_start = datetime.now()
    last_update = datetime.now()
    print_status(elite_individual, original_individual, evaluations, t_start)

    while datetime.now() - t_start < DURATION and not should_stop:
        if datetime.now() - last_update > UPDATE_INTERVAL:
            print_status(elite_individual, original_individual, evaluations, t_start)
            last_update = datetime.now()

        for index_, individual in enumerate(population):
            is_ready = individual.is_evaluation_ready
            if is_ready:
                logger.debug(f"Individual {index_} is ready")
                evaluations += 1

                if individual.get_fitness() > elite_individual.get_fitness():
                    elite_individual = individual.clone()
                    print_status(elite_individual, original_individual, evaluations, t_start)
                    store_elite(elite_individual, evaluations, elite_individual.get_fitness())

                    logger.debug(f"New elite individual: {index_} {json.dumps(individual.get_raw_fitness())}")
                else:
                    logger.debug(
                        f"Individual {index_} {individual.get_fitness()} isnt better than elite {elite_individual.get_fitness()}"
                    )

                individual.set_genes(elite_individual.genes)
                mutate_individual(individual)
                individual.trigger_fitness_evaluation(force=True)

        sleep(1)

    if should_stop:
        logger.info("Search interrupted by user. Waiting for remaining evaluations to finish...")
    else:
        logger.info("Finished main loop. Waiting for remaining evaluations to finish")

    while not all(individual.is_evaluation_ready for individual in population):
        sleep(1)
    logger.info("Finished waiting for remaining evaluations to finish")

    for individual in population:
        if individual.get_fitness() > elite_individual.get_fitness():
            elite_individual = individual.clone()
            logger.info(f"New elite individual: {json.dumps(individual.get_raw_fitness())}")

    logger.info(f"Elite individual: {json.dumps(elite_individual.get_raw_fitness())}")

    if should_stop:
        logger.info("Search completed after interruption. Final results saved.")


def print_status(
    elite_individual: Individual, original_individual: Individual, evaluations: int, t_start: datetime
) -> None:
    time_elapsed = datetime.now() - t_start
    time_left = DURATION - time_elapsed
    time_progress = time_elapsed.total_seconds() / DURATION.total_seconds()
    gene_distance = (
        sum((elite_individual.genes[i] - original_individual.genes[i]) ** 2 for i in range(elite_individual.n_genes))
        ** 0.5
    )

    evals_str = f"{evaluations=:6d}"
    distance_str = f"distance={gene_distance:5.2f}"
    elite_score_str = f"elite_score={elite_individual.get_fitness():8.2f}"
    elapsed_str = f"elapsed={time_elapsed.total_seconds() / 60:5.2f}m"
    left_str = f"left={time_left.total_seconds() / 60:5.2f}m"
    progress_str = f"({time_progress:5.2%})"
    tokens = [evals_str, distance_str, elite_score_str, elapsed_str, left_str, progress_str]
    logger.info("   ".join(tokens))


def mutate_individual(individual: Individual) -> None:
    genes = individual.genes
    random_gene_index = random.randint(0, individual.n_genes - 1)
    direction = random.choice([-1, 1])
    genes[random_gene_index] += direction * STEP_SIZE
    individual.set_genes(genes)


def store_elite(individual: Individual, generation_count: int, elite_score: float) -> None:
    base_path = "results/local_search/"
    os.makedirs(base_path, exist_ok=True)

    with open(f"{base_path}/elite_individual__{RUN_ID}__{generation_count}_score_{elite_score}.json", "wt") as f:
        f.write(json.dumps(individual.settings, indent=2))
