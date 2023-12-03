from population import Population


def main():
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
