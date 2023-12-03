import json
from copy import copy
from random import choice, random, uniform

import config
from agent import Agent


class Individual:
    def __init__(self, agent=None):
        self._agent = agent or Agent()
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
        copy_agent = self._agent.clone()
        new = Individual(agent=copy_agent)
        new.n_genes = self.n_genes
        new.genes = copy(self.genes)

        return new


class Population:
    def __init__(self):
        self.population_size = config.POPULATION_SIZE
        self._init_population()

        self.crossover_chance = config.CROSSOVER_RATE
        self.mutation_chance = config.MUTATION_RATE

        self.generations = 0

    def _init_population(self):
        self.population = [Individual() for _ in range(self.population_size)]

    def evaluate_population_fitness(self):
        for individual in self.population:
            individual.trigger_fitness_evaluation()

        print(f"{self.generations:4d}/{config.N_GENERATIONS:4d}", end=" ", flush=True)
        scores = [individual.get_fitness() for individual in self.population]
        print(f"{min(scores):6d} {sum(scores) / len(scores):6.2f} {max(scores):6d}", end=" ")
        print()

        self.elite_individual = self.get_elite_individual()

    def start_generation(self):
        pass

    def end_generation(self):
        self.generations += 1

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
        for individual in self.population:
            if random() > self.crossover_chance:
                continue

            child = Individual()
            mate = choice(self.population)

            for i in range(individual.n_genes):
                if random() > 0.5:
                    child.genes[i] = individual.genes[i]
                else:
                    child.genes[i] = mate.genes[i]

            self.population.append(child)

    def mutation(self):
        for individual in self.population:
            if random() > self.mutation_chance:
                continue

            for i in range(individual.n_genes):
                if random() > self.mutation_chance / individual.n_genes:
                    continue

                # Changes the value by up to 10% in either direction
                individual.genes[i] *= uniform(0.9, 1.1)

        for i in range(config.ELITE_MUTATIONS):
            individual = self.elite_individual.clone()

            changed = 0
            while changed < i + 1:
                for i in range(individual.n_genes):
                    if random() > self.mutation_chance / individual.n_genes:
                        continue

                    individual.genes[i] *= uniform(0.9, 1.1)
                    changed += 1

            self.population.append(individual)

    def store_elite_individual(self):
        with open(f"elite_individual__{self.generations}.json", "wt") as f:
            f.write(json.dumps(self.elite_individual._agent.settings))
