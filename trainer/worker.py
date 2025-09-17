import inspect
import json
import signal
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
    def signal_handler(signum, frame):
        logger.info(f"Worker received signal {signum}. HI Momo")

        # Use inspect to get the calling frame and access local variables
        current_frame = inspect.currentframe()
        try:
            # Walk up the call stack to find the single_worker_loop frame
            while current_frame:
                if current_frame.f_code.co_name == "single_worker_loop":
                    # Get local variables from the single_worker_loop frame
                    local_vars = current_frame.f_locals
                    task_key = local_vars.get("task_key")
                    redis = local_vars.get("redis")

                    if task_key and redis:
                        logger.info(f"Requeuing task {task_key} due to signal")
                        # We need to get the task to determine the result_key
                        task_raw = redis.get(task_key)
                        if task_raw:
                            task = TaskSerializer.from_json(task_raw.decode())
                            if task:
                                result_key = f"result:{task.instance_id}:status"
                                redis.lpush("tasks", task_key)
                                redis.hset(result_key, "status", "pending")
                                logger.info(f"Requeued task {task_key} due to signal")
                            else:
                                logger.warning(f"Failed to deserialize task {task_key} for requeue")
                        else:
                            logger.warning(f"Task data not found for {task_key} during signal handling")
                    else:
                        logger.warning("No current task_key or redis connection found in signal handler")
                    break
                current_frame = current_frame.f_back
        finally:
            logger.info(f"Releasing lock {lock=}")

            # Wait to be acquired before releasing
            while not lock.acquire(timeout=10):
                time.sleep(0.5)

            logger.info(f"Lock released {lock=}")

            # Clean up frame reference to avoid circular references
            del current_frame

    signal.signal(signal.SIGINT, signal_handler)

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
            run_task(task, str(task_key))
        else:
            raise Exception(f"Failed to deserialize task data for {task_key=}")


def run_task(task: TaskInstance, task_key: str) -> None:
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
