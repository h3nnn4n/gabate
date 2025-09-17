from datetime import datetime
from random import random, uniform

import config
from agent import Individual
from logging_config import get_logger
from random_search import RandomSearch

logger = get_logger(__name__)


def forever_search():
    fs = ForeverSearch()
    fs.run()


class ForeverSearch(RandomSearch):
    def __init__(self):
        self.population_size = config.POPULATION_SIZE
        self.population = self.build_population()

        self.new_population = []

        self.elite_genes = self.population[0].genes
        self.elite_score = 0
        self.elite_individual = self.population[0]

        self.generation_count = 0

    def initialize_population(self):
        logger.info("")
        logger.info("Initializing population")
        for i in range(len(self.population)):
            logger.info(f"Running random search {i+1} of {len(self.population)}")
            elite_genes = RandomSearch().run()
            self.population[i].genes = elite_genes
            self.population[i]._agent.set_weights(elite_genes)

            self.population[i].trigger_fitness_evaluation()
            individual_score = self.population[i].get_fitness()
            if individual_score > self.elite_score:
                self.elite_genes = elite_genes
                self.elite_score = individual_score
                self.elite_individual = self.population[i]

        logger.info("finished initializing population")
        logger.info("")

    def run(self):
        self.initialize_population()

        while True:
            self.run_generation()

            if self.generation_count > 10:
                break

    def run_generation(self):
        t_start = datetime.now()

        self.population[0].genes = self.elite_genes
        self.population[0]._agent.set_weights(self.elite_genes)

        for i in range(len(self.population)):
            self.mutate_individual(self.population[i])

        for individual in self.population:
            individual.trigger_fitness_evaluation()

        scores = [individual.get_fitness() for individual in self.population]

        generation_duration = (datetime.now() - t_start).total_seconds()
        diversity = self.get_diversity()
        self.generation_count += 1

        self.elite_individual = self.update_elite()
        self.store_elite()

        logger.info(
            f"{self.generation_count:4d}   min={min(scores):7d}   mean={sum(scores) / len(scores):8.2f}   max={max(scores):7d}   {diversity=:7.2f}   {generation_duration=:7.2f}   elite={self.elite_score=:7.2f}"
        )

    def mutate_individual(self, individual: Individual):
        for i in range(individual.n_genes):
            if random() > config.MUTATION_RATE:
                continue

            individual.genes[i] *= uniform(0.95, 1.05)

        individual._agent.set_weights(individual.genes)
