import argparse

from random_search import random_search

from genetic_algorithm import genetic_algorithm


def main():
    parser = argparse.ArgumentParser(description="Train gabate.")
    parser.add_argument(
        "mode",
        type=str,
        help="The training mode to use to train gabate.",
        choices=["genetic_algorithm", "random_search"],
    )

    args = parser.parse_args()

    match args.mode:
        case "genetic_algorithm":
            genetic_algorithm()
        case "random_search":
            random_search()
        case _:
            raise ValueError(f"Invalid mode: {args.mode}")


if __name__ == "__main__":
    main()
