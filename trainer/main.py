import config
from population import Population


def main():
    print("settings")
    print(f"  N_GENERATIONS: {config.N_GENERATIONS}")
    print(f"POPULATION_SIZE: {config.POPULATION_SIZE}")
    print(f"  N_AGENT_EVALS: {config.N_AGENT_EVALS}")
    print(f" CROSSOVER_RATE: {config.CROSSOVER_RATE}")
    print(f"  MUTATION_RATE: {config.MUTATION_RATE}")
    print()
    print("starting...")

    population = Population()

    for generation in range(config.N_GENERATIONS):
        population.start_generation()
        population.evaluate_population_fitness()
        population.selection()
        population.crossover()
        population.mutation()
        population.end_generation()

    print("finished")


if __name__ == "__main__":
    main()
