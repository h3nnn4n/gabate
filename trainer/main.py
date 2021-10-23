from population import Population
from utils import get_n_workers, ping


def main():
    n_nodes, n_workers = get_n_workers()
    print(f"running with {n_nodes} nodes and {n_workers} workers")

    assert ping()

    population = Population()
    population.evaluate_population_fitness()


if __name__ == "__main__":
    main()
