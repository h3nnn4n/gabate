import argparse

from evaluator import evaluator
from forever_search import forever_search
from genetic_algorithm import genetic_algorithm
from grid_searcher import grid_searcher
from random_search import random_search
from record_breaker import record_breaker
from worker import worker_loop


def main():
    parser = argparse.ArgumentParser(description="Train gabate")
    parser.add_argument(
        "--worker",
        action="store_true",
        help="Run as an worker, which will run the agent evaluation tasks.",
    )
    parser.add_argument(
        "mode",
        type=str,
        nargs="?",
        help="The training mode to use to train gabate.",
        choices=["genetic_algorithm", "random_search", "forever_search", "evaluator", "grid_searcher", "record_breaker"],
    )
    parser.add_argument(
        "--individual",
        type=str,
        help="The path to the individual to evaluate.",
        default=None,
    )

    args = parser.parse_args()

    if args.worker:
        return worker_loop()

    if args.mode is None:
        parser.error("mode is required when not running as worker")

    match args.mode:
        case "genetic_algorithm":
            genetic_algorithm()
        case "random_search":
            random_search()
        case "forever_search":
            forever_search()
        case "evaluator":
            if args.individual is None:
                raise ValueError("Individual path is required for evaluator mode")

            evaluator(args.individual)
        case "grid_searcher":
            if args.individual is None:
                raise ValueError("Individual path is required for grid searcher mode")

            grid_searcher(args.individual)
        case "record_breaker":
            record_breaker(args.individual)
        case _:
            raise ValueError(f"Invalid mode: {args.mode}")


if __name__ == "__main__":
    main()
