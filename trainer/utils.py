from worker import worker


def get_n_workers():
    n_workers = 0
    nodes_data = worker.control.inspect().stats()

    for node in nodes_data.values():
        n_workers += node["pool"]["max-concurrency"]

    return len(nodes_data), n_workers
