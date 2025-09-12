import json

from agent import Individual


def evaluator(individual_path: str):
    with open(individual_path, "r") as f:
        agent_settings = json.load(f)

    genes = agent_settings["weights"]

    individual = Individual()
    individual.genes = genes
    individual._agent.set_weights(genes)
    individual.trigger_fitness_evaluation()

    print(individual.get_fitness())
