import json
import threading
import uuid

import config
from agent import Individual

best_fitness = 0
run_id = str(uuid.uuid4())
file_lock = threading.Lock()


def record_breaker(individual_path: str) -> None:
    threads = []

    print_fitness_header()

    for i in range(config.POPULATION_SIZE):
        thread = threading.Thread(target=loop, args=(individual_path,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def load_agent(individual_path: str) -> Individual:
    with open(individual_path, "r") as f:
        agent_settings = json.load(f)

    genes = agent_settings["weights"]

    individual = Individual()
    individual.set_genes(genes)
    return individual


def loop(individual_path: str) -> None:
    global best_fitness

    individual = load_agent(individual_path)

    while True:
        individual.evaluate_fitness(force=True)
        raw_fitness = individual.get_raw_fitness()

        if raw_fitness["max"] > best_fitness:
            best_fitness = raw_fitness["max"]

        print_pretty_fitness(raw_fitness)

        store_data(raw_fitness)


def store_data(raw_fitness: dict) -> None:
    raw_scores = raw_fitness["raw"]
    with file_lock:
        with open(f"results/{run_id}.txt", "a+t") as f:
            for score in raw_scores:
                f.write(f"{score}\n")


def print_pretty_fitness(raw_fitness: dict) -> None:
    print(
        f"{raw_fitness['min']:8} {raw_fitness['avg']:10.2f} {raw_fitness['median']:10.2f} {raw_fitness['max']:8}    {best_fitness:8}"
    )


def print_fitness_header() -> None:
    print(f"{'min':8} {'avg':12} {'median':12} {'max':8}    {'best':8}")
