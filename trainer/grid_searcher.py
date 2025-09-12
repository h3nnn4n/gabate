import json
from pprint import pprint

from agent import Individual

GRID_SEARCH_RANGE = 5.0
GRID_SEARCH_STEP = 0.5


def grid_searcher(individual_path: str):
    individual = load_agent(individual_path)

    run_grid_search(individual)


def load_agent(individual_path: str):
    with open(individual_path, "r") as f:
        agent_settings = json.load(f)

    genes = agent_settings["weights"]

    print("Evaluating initial individual")

    individual = Individual()
    individual.set_genes(genes)
    individual.trigger_fitness_evaluation()
    fitness = individual.get_raw_fitness()

    print("initial fitness:")
    pprint(fitness)
    print()

    return individual


def run_grid_search(individual: Individual):
    test_individuals = []
    elite_individual = individual.clone()

    for i in range(individual.n_genes):
        print()
        print(f"running grid search for gene {i}/{individual.n_genes}  elite_score: {elite_individual.get_fitness()}")

        test_individuals = []
        grid_range = GRID_SEARCH_RANGE * 2
        n_grid_steps = int(grid_range // GRID_SEARCH_STEP) + 1  # Rather search a bit more than a bit less

        for j in range(n_grid_steps):
            gene_value = j * GRID_SEARCH_STEP - GRID_SEARCH_RANGE
            new_genes = elite_individual.genes.copy()
            new_genes[i] = gene_value
            test_individual = elite_individual.clone()
            test_individual.set_genes(new_genes)
            test_individuals.append(test_individual)

        for test_individual in test_individuals:
            test_individual.trigger_fitness_evaluation()

        scores = [test_individual.get_fitness() for test_individual in test_individuals]
        fitness = min(scores)

        for test_individual, score in zip(test_individuals, scores):
            if score > elite_individual.get_fitness():
                elite_individual = test_individual.clone()
                print(f"new elite individual {score=}")

        print(f"iteration {i} elite_score:")
        pprint(elite_individual.get_raw_fitness())
        
    return elite_individual
