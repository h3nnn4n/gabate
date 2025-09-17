import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(is_worker: bool = False) -> None:
    """
    Set up logging configuration for the trainer.

    Args:
        is_worker: If True, log file will be named 'worker_timestamp.log',
                  otherwise 'trainer_timestamp.log'
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_prefix = "worker" if is_worker else "trainer"
    log_file = log_dir / f"{log_prefix}_{timestamp}.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured. Log file: {log_file}")
    logger.info(f"Running in {'worker' if is_worker else 'trainer'} mode")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
