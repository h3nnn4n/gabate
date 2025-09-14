import json
from multiprocessing import Pool
from time import sleep

import config
from queueer.task import TaskInstance, TaskSerializer
from utils import get_redis

WORKER_CONCURRENCY = config.WORKER_CONCURRENCY  # type: ignore


def worker_loop() -> None:
    print(f"Running worker with {WORKER_CONCURRENCY=}")

    with Pool(WORKER_CONCURRENCY) as pool:
        pool.map(single_worker_loop, range(WORKER_CONCURRENCY))


def single_worker_loop(_worker_id: int) -> None:
    redis = get_redis()

    while True:
        task_key = redis.lpop("tasks")

        if task_key is None:
            sleep(1)
            continue

        task_raw = redis.get(task_key)  # type: ignore
        if task_raw is None:
            sleep(1)
            continue

        task = TaskSerializer.from_json(task_raw.decode())  # type: ignore
        if task:
            run_task(task)
        else:
            sleep(1)


def run_task(task: TaskInstance) -> None:
    redis = get_redis()
    result_key = f"result:{task.instance_id}:status"

    redis.hset(result_key, "status", "running")

    args = task.args or []
    kwargs = task.kwargs or {}

    print(f"running task {task.name=} {task.instance_id=}")

    try:
        result = task.callable(*args, **kwargs)
        print(f"finished task {task.name=} {task.instance_id=}")
    except Exception as e:
        print(f"failed task {task.name=} {task.instance_id=} with exception: {e}")
        redis.hset(result_key, "status", "failed")
        redis.hset(result_key, "result", json.dumps({"error": str(e)}))
    else:
        redis.hset(result_key, "status", "finished")
        redis.hset(result_key, "result", json.dumps(result))
