from datetime import datetime
from random import random, uniform

import config
from agent import Individual


def random_search():
    rs = RandomSearch()
    rs.run()


class RandomSearch:
    def __init__(self):
        self.population_size = config.POPULATION_SIZE
        self.population = self.build_population()
        self.elite_genes = self.population[0].genes
        self.elite_score = 0

        self.generation_count = 0

    def run(self):
        for _ in range(config.N_GENERATIONS):
            self.run_generation()

    def run_generation(self):
        t_start = datetime.now()
        for individual in self.population:
            individual.trigger_fitness_evaluation()

        scores = [individual.get_fitness() for individual in self.population]

        generation_duration = (datetime.now() - t_start).total_seconds()
        diversity = self.get_diversity()
        self.generation_count += 1

        self.elite = self.update_elite()

        self.population = self.build_population()
        self.population[0].genes = self.elite_genes
        self.mutate_individual(self.population[0])

        print(f"{self.generation_count:4d}/{config.N_GENERATIONS:4d}   ", end=" ")
        print(f"min={min(scores):7d}   ", end=" ")
        print(f"mean={sum(scores) / len(scores):8.2f}   ", end=" ")
        print(f"max={max(scores):7d}   ", end=" ")
        print(f"{diversity=:7.2f}   ", end=" ")
        print(f"{generation_duration=:7.2f}   ", end=" ")
        print(f"elite={self.elite_score=:7.2f}   ", end=" ")
        print(flush=True)

    def build_population(self) -> list[Individual]:
        return [Individual() for _ in range(self.population_size)]

    def get_diversity(self) -> float:
        n_genes = self.population[0].n_genes
        value = 0
        count = 0

        for i in range(self.population_size):
            individual_a = self.population[i]
            for j in range(self.population_size):
                if i == j:
                    continue

                individual_b = self.population[j]
                count += 1

                for k in range(individual_a.n_genes):
                    value += abs(individual_a.genes[k] - individual_b.genes[k]) / n_genes

        return value / count

    def update_elite(self) -> Individual:
        new_elite = max(self.population, key=lambda x: x.get_fitness())
        new_elite_score = new_elite.get_fitness()

        if new_elite_score > self.elite_score:
            self.elite_genes = new_elite.genes
            self.elite_score = new_elite_score

    def mutate_individual(self, individual: Individual):
        for i in range(individual.n_genes):
            if random() > config.MUTATION_RATE:
                continue

            individual.genes[i] *= uniform(0.9, 1.1)
