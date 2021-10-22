from worker import worker


@worker.task
def add(x, y):
    return x + y
