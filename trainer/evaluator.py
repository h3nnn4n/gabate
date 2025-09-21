import json

from agent import load_agent
from logging_config import get_logger

logger = get_logger(__name__)


def evaluator(individual_path: str):
    individual = load_agent(individual_path, evaluate=True)

    raw_fitness = individual.get_raw_fitness()

    logger.info(
        f"min={raw_fitness['min']:8} avg={raw_fitness['avg']:10.2f} median={raw_fitness['median']:10.2f} max={raw_fitness['max']:8}"
    )
