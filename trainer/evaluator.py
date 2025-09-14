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

    raw_fitness = individual.get_raw_fitness()

    print(
        f"min={raw_fitness['min']:8} avg={raw_fitness['avg']:10.2f} median={raw_fitness['median']:10.2f} max={raw_fitness['max']:8}"
    )
