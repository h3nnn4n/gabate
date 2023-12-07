from datetime import datetime

import config
from agent import Individual


def random_search():
    rs = RandomSearch()
    rs.run()


class RandomSearch:
    def __init__(self):
        self.population_size = config.POPULATION_SIZE
        self.population = self.build_population()

        self.generations = 1
        self.generation_time = datetime.now()

    def run(self):
        for individual in self.population:
            individual.trigger_fitness_evaluation()

        scores = [individual.get_fitness() for individual in self.population]

        generation_time = datetime.now()
        generation_duration = (generation_time - self.generation_time).total_seconds()
        diversity = self.get_diversity()

        print(f"{self.generations:4d}/{config.N_GENERATIONS:4d}", end=" ", flush=True)
        print(f"{min(scores):7d} {sum(scores) / len(scores):8.2f} {max(scores):7d}", end=" ")
        print(f"{diversity:7.2f} {generation_duration:7.2f}", end="")
        print()

    def build_population(self) -> list[Individual]:
        return [Individual() for _ in range(self.population_size)]

    def get_diversity(self) -> float:
        # FIXME: Should be a config
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
