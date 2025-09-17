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

            for i, lock in enumerate(locks):
                logger.info(f"Waiting for worker {i} to finish")

                while not lock.acquire(timeout=1):
                    logger.debug(f"Still waiting for worker {i} to finish...")
                    time.sleep(1)

                lock.release()
                logger.info(f"Worker {i} finished {lock=}")


def single_worker_loop(_worker_id: int, lock) -> None:
    shutdown_requested = False

    def signal_handler(signum, frame):
        nonlocal shutdown_requested
        logger.info(f"Worker {_worker_id} received signal: {signum}")
        shutdown_requested = True

        # Iterate over frames to find the task_key to enqueue it back
        current_frame = inspect.currentframe()
        try:
            while current_frame:
                if current_frame.f_code.co_name == "single_worker_loop":
                    local_vars = current_frame.f_locals
                    task_key = local_vars.get("task_key")
                    redis = local_vars.get("redis")
                    task = local_vars.get("task")

                    if task_key and redis and task:
                        logger.info(f"Requeuing task {task_key} due to signal")
                        try:
                            result_key = f"result:{task.instance_id}:status"
                            redis.hset(result_key, "status", "pending")
                            redis.lpush("tasks", task_key)
                            logger.info(f"Requeued task {task_key} due to signal")
                        except Exception as e:
                            logger.error(f"Failed to requeue task {task_key}: {e}")
                    else:
                        logger.warning("No current task_key or redis connection found in signal handler")
                    break
                current_frame = current_frame.f_back
        finally:
            # Clean up frame reference to avoid circular references
            del current_frame

    signal.signal(signal.SIGINT, signal_handler)

    redis = get_redis()

    task_key = None
    task = None

    try:
        while not shutdown_requested:
            task_key = redis.lpop("tasks")

            if task_key is None:
                time.sleep(0.1)
                continue

            task_raw = redis.get(task_key)  # type: ignore
            if task_raw is None:
                logger.error(f"task data not found for {task_key=}")
                task_key = None
                continue

            task = TaskSerializer.from_json(task_raw.decode())  # type: ignore
            if task:
                run_task(task, str(task_key))

                task_key = None
                task = None
            else:
                logger.error(f"Failed to deserialize task data for {task_key=}")
                task_key = None

    except Exception as e:
        logger.error(f"Worker {_worker_id} encountered error: {e}")
    finally:
        logger.info(f"Worker {_worker_id} acquiring lock to signal completion")
        lock.acquire()
        logger.info(f"Worker {_worker_id} has acquired lock and is exiting")


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
