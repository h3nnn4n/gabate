import argparse

from evaluator import evaluator
from forever_search import forever_search
from genetic_algorithm import genetic_algorithm
from random_search import random_search


def main():
    parser = argparse.ArgumentParser(description="Train gabate.")
    parser.add_argument(
        "mode",
        type=str,
        help="The training mode to use to train gabate.",
        choices=["genetic_algorithm", "random_search", "forever_search", "evaluator"],
    )
    parser.add_argument(
        "--individual",
        type=str,
        help="The path to the individual to evaluate.",
        default=None,
    )

    args = parser.parse_args()

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
        case _:
            raise ValueError(f"Invalid mode: {args.mode}")


if __name__ == "__main__":
    main()
