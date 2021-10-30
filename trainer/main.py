from population import Population
from utils import get_n_workers, ping


def main():
    n_nodes, n_workers = get_n_workers()
    print(f"running with {n_nodes} nodes and {n_workers} workers")

    assert ping()

    population = Population()

    for generation in range(10):
        print(f"starting gen {generation}")
        population.evaluate_population_fitness()
        population.print_pop_state()
        population.selection()
        population.crossover()
        population.mutation()

    print("finished")
    population.evaluate_population_fitness()
    population.print_pop_state()


if __name__ == "__main__":
    main()
