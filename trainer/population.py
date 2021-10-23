from agent import Agent


class Individual:
    def __init__(self):
        self._agent = Agent()

    def evaluate_fitness(self):
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

    def _init_population(self):
        self.population = [Individual() for _ in range(self.population_size)]

    def evaluate_population_fitness(self):
        for individual in self.population:
            individual.trigger_fitness_evaluation()

        for individual in self.population:
            print(individual.get_fitness())
