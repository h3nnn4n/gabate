import os


def ensure_folder_exists(path: str) -> None:
    try:
        os.makedirs(path)
    except OSError:
        pass
