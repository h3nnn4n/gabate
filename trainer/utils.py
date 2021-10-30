import json

from worker import worker


def get_n_workers():
    n_workers = 0
    nodes_data = worker.control.inspect().stats()

    for node in nodes_data.values():
        n_workers += node["pool"]["max-concurrency"]

    return len(nodes_data), n_workers


def ping():
    _, n_workers = get_n_workers()
    data = dict(ping="foobar")
    results = [worker.send_task("tasks.evaluate_agent", args=[data]) for _ in range(n_workers * 4)]

    for n, result in enumerate(results):
        parsed_response = json.loads(result.get())
        assert parsed_response["pong"] == "foo bar"

    return True
