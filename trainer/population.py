import json
import csv
from copy import copy
from datetime import datetime
from random import choice, random, uniform

import config
import utils
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

        # Short circuit fitness to zero if IA fails to score anything during any evals
        if result["min"] == 0:
            return 0

        match config.FITNESS_MODE.upper():
            case "MAX":
                return result["max"]
            case "MIN":
                return result["min"]
            case "MEDIAN":
                return result["median"]
            case "SUM":
                return sum(result["raw"])
            case "AVG":
                return sum(result["raw"]) / len(result["raw"])
            case _:
                raise ValueError(f"{config.FITNESS_MODE} is not a valid option")

    def clone(self):
        copy_agent = self._agent.clone()
        new = Individual(agent=copy_agent)
        new.n_genes = self.n_genes
        new.genes = copy(self.genes)

        return new


class Population:
    def __init__(self):
        self.population_size = config.POPULATION_SIZE
        self.population = self.build_population()

        self.crossover_chance = config.CROSSOVER_RATE
        self.mutation_chance = config.MUTATION_RATE

        self.generations = 0

        self.started_at = datetime.now()
        self.pop_id = f"{self.started_at:%Y%m%d_%H%M%S}_{self.population_size}"

        utils.ensure_folder_exists(f"results/{self.pop_id}")

        self.store_experiment_details()

    def build_population(self) -> list[Individual]:
        return [Individual() for _ in range(self.population_size)]

    def evaluate_population_fitness(self):
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

        self.elite_individual = self.get_elite_individual()

        self.store_population_statistics()

    def start_generation(self):
        self.generation_time = datetime.now()

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
        with open(f"results/{self.pop_id}/elite_individual__{self.generations}.json", "wt") as f:
            f.write(json.dumps(self.elite_individual._agent.settings))

    def store_experiment_details(self) -> None:
        with open(f"results/{self.pop_id}/experiment_details.json", "wt") as f:
            f.write(
                json.dumps(
                    {
                        "n_generations": config.N_GENERATIONS,
                        "population_size": self.population_size,
                        "n_agents_evals": config.N_AGENT_EVALS,
                        "crossover_chance": self.crossover_chance,
                        "mutation_chance": self.mutation_chance,
                        "elite_mutations": config.ELITE_MUTATIONS,
                        "fitness_mode": config.FITNESS_MODE,
                        "started_at": f"{self.started_at:%Y-%m-%d %H:%M:%S}",
                    }
                )
            )

    def store_population_statistics(self) -> None:
        scores = [individual.get_fitness() for individual in self.population]

        generation_time = datetime.now()
        generation_duration = (generation_time - self.generation_time).total_seconds()

        with open(f"results/{self.pop_id}/stats.csv", "a+t") as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(
                [
                    self.generations + 1 / config.N_GENERATIONS,
                    self.generations + 1,
                    min(scores),
                    sum(scores) / len(scores),
                    max(scores),
                    self.get_diversity(),
                    generation_duration,
                ]
            )

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
