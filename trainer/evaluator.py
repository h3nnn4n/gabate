import json

from agent import Individual


def evaluator(individual_path: str):
    genes = json.load(open(individual_path))["weights"]

    individual = Individual()
    individual.genes = genes
    individual._agent.set_weights(genes)
    individual.trigger_fitness_evaluation()

    print(individual.get_fitness())
