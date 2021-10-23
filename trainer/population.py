from copy import copy
from random import choice, random, uniform

from agent import Agent


class Individual:
    def __init__(self):
        self._agent = Agent()
        self.id = self._agent.id
        self.n_genes = 14 * 3
        self.genes = [uniform(-5, 5) for _ in range(self.n_genes)]

    def evaluate_fitness(self):
        self._agent.set_weights(self.genes)
        self._agent.trigger_eval()
        self._agent.get_fitness()

    def trigger_fitness_evaluation(self):
        self._agent.trigger_eval()

    def get_fitness(self):
        result = self._agent.get_fitness()

        if result["min"] == 0:
            return 0

        return result["max"]

    def clone(self):
        new = Individual()
        new.n_genes = self.n_genes
        new.genes = copy(self.genes)

        return new


class Population:
    def __init__(self):
        self.population_size = 5
        self._init_population()

        self.crossover_chance = 0.2
        self.mutation_chance = 0.05

    def _init_population(self):
        self.population = [Individual() for _ in range(self.population_size)]

    def evaluate_population_fitness(self):
        for individual in self.population:
            individual.trigger_fitness_evaluation()

    def print_pop_state(self):
        print(" ".join([str(individual.get_fitness()) for individual in self.population]))

    def selection(self):
        _new_pop = [self.get_elite_individual().clone()]

        while len(_new_pop) < self.population_size:
            p1 = choice(self.population)
            p2 = choice(self.population)

            if p1.get_fitness() == 0 and p2.get_fitness() == 0:
                _new_pop.append(Individual())
            elif uniform(0.7, 1) * p1.get_fitness() > uniform(0.7, 1) * p2.get_fitness():
                _new_pop.append(p1.clone())
            else:
                _new_pop.append(p2.clone())

        self.population = _new_pop

    def get_elite_individual(self):
        return max(self.population, key=lambda individual: individual.get_fitness())

    def crossover(self):
        pass

    def mutation(self):
        for individual in self.population:
            if random() > self.mutation_chance:
                continue

            for i in range(individual.n_genes):
                if random() > self.mutation_chance / individual.n_genes:
                    continue

                # Changes the value by up to 10% in either direction
                individual.genes[i] *= uniform(0.9, 1.1)
