import json
import time
from multiprocessing import Manager, Pool

import config
from logging_config import get_logger
from queueer.task import TaskInstance, TaskSerializer
from utils import get_redis

logger = get_logger(__name__)

WORKER_CONCURRENCY = config.WORKER_CONCURRENCY  # type: ignore


def worker_loop() -> None:
    logger.info(f"Running worker with {WORKER_CONCURRENCY=}")

    with Manager() as manager:
        locks = [manager.Lock() for _ in range(WORKER_CONCURRENCY)]
        try:
            with Pool(WORKER_CONCURRENCY) as pool:
                pool.starmap(single_worker_loop, [(i, locks[i]) for i in range(WORKER_CONCURRENCY)])
        except KeyboardInterrupt:
            logger.info(f"Master received KeyboardInterrupt. HI Momo")
            for lock in locks:
                logger.info(f"Locking worker {lock=}")
                lock.acquire()

            for lock in locks:
                logger.info(f"Waiting for worker to finish {lock=}")
                while not lock.acquire(timeout=10):
                    time.sleep(0.5)
                lock.release()
                logger.info(f"Worker finished {lock=}")


def single_worker_loop(_worker_id: int, lock) -> None:
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
            try:
                run_task(task, str(task_key), lock)
            except KeyboardInterrupt:
                logger.info(f"Worker {_worker_id=} received KeyboardInterrupt")
                # lock.acquire()
        else:
            raise Exception(f"Failed to deserialize task data for {task_key=}")


def run_task(task: TaskInstance, task_key: str, lock) -> None:
    force_exit = False

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
    except KeyboardInterrupt:
        logger.info(f"Task {task.name=} {task.instance_id=} received KeyboardInterrupt. Sending task back to the queue")
        redis.lpush("tasks", task_key)
        redis.hset(result_key, "status", "pending")
        force_exit = True
    else:
        redis.hset(result_key, "result", json.dumps(result))
        redis.hset(result_key, "status", "finished")
    finally:
        if force_exit:
            lock.release()
