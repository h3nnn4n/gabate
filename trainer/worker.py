import json
from multiprocessing import Pool

import config
from logging_config import get_logger
from queueer.task import TaskInstance, TaskSerializer
from utils import get_redis

logger = get_logger(__name__)

WORKER_CONCURRENCY = config.WORKER_CONCURRENCY  # type: ignore


def worker_loop() -> None:
    logger.info(f"Running worker with {WORKER_CONCURRENCY=}")

    with Pool(WORKER_CONCURRENCY) as pool:
        pool.map(single_worker_loop, range(WORKER_CONCURRENCY))


def single_worker_loop(_worker_id: int) -> None:
    redis = get_redis()

    while True:
        task_key = redis.lpop("tasks")

        if task_key is None:
            continue

        task_raw = redis.get(task_key)  # type: ignore
        if task_raw is None:
            raise Exception(f"task data not found for {task_key=}")

        task = TaskSerializer.from_json(task_raw.decode())  # type: ignore
        if task:
            run_task(task)
        else:
            raise Exception(f"Failed to deserialize task data for {task_key=}")


def run_task(task: TaskInstance) -> None:
    redis = get_redis()
    result_key = f"result:{task.instance_id}:status"

    redis.hset(result_key, "status", "running")

    args = task.args or []
    kwargs = task.kwargs or {}

    logger.info(f"running task {task.name=} {task.instance_id=}")

    try:
        result = task.callable(*args, **kwargs)
        logger.info(f"finished task {task.name=} {task.instance_id=}")
    except Exception as e:
        logger.info(f"failed task {task.name=} {task.instance_id=} with exception: {e}")
        redis.hset(result_key, "result", json.dumps({"error": str(e)}))
        redis.hset(result_key, "status", "failed")
    else:
        redis.hset(result_key, "result", json.dumps(result))
        redis.hset(result_key, "status", "finished")
