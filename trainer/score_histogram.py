import argparse

import matplotlib.pyplot as plt
import seaborn as sns

from logging_config import get_logger

logger = get_logger(__name__)


def plot_histogram(input_file, output_file):
    try:
        with open(input_file, "r") as f:
            numbers = [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"Error: File '{input_file}' not found.")
        return
    except ValueError:
        logger.error("Error: File contains non-integer values.")
        return

    if not numbers:
        logger.error("Error: No valid integers found in the file.")
        return

    plt.figure(figsize=(10, 6))
    sns.histplot(numbers, kde=True, bins=30)
    plt.title("Histogram of Integer Values")
    plt.xlabel("Values")
    plt.ylabel("Frequency")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    logger.info(f"Histogram saved to '{output_file}'")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot a histogram from a file of integers.")
    parser.add_argument("input_filename", type=str, help="Input file containing integer values, one per line.")
    parser.add_argument(
        "--output_filename", type=str, default="histogram.png", help="Output image file for the histogram."
    )
    args = parser.parse_args()

    plot_histogram(args.input_filename, args.output_filename)
