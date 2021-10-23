from agent import Agent
from random import choice, random, uniform


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
        return self._agent.get_fitness()["max"]


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
        _new_pop = []

        for _ in range(self.population_size):
            p1 = choice(self.population)
            p2 = choice(self.population)

            if random() * p1.get_fitness() > random() * p2.get_fitness():
                _new_pop.append(p1)
            else:
                _new_pop.append(p2)

        self.population = _new_pop

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
