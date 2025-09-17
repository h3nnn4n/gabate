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
        shutdown_event = manager.Event()

        def master_signal_handler(signum, frame):
            logger.info(f"Master received signal {signum}")
            shutdown_event.set()

        original_handler = signal.signal(signal.SIGINT, master_signal_handler)

        try:
            with Pool(WORKER_CONCURRENCY) as pool:
                pool.starmap(single_worker_loop, [(i, locks[i], shutdown_event) for i in range(WORKER_CONCURRENCY)])
        except KeyboardInterrupt:
            # This shouldn't happen, but just in case
            logger.info(f"Master received KeyboardInterrupt in except block")
            shutdown_event.set()
        finally:
            signal.signal(signal.SIGINT, original_handler)

            logger.info("Waiting for workers to complete immediate shutdown...")

            time.sleep(0.2)

            for i, lock in enumerate(locks):
                logger.info(f"Waiting for worker {i} to finish")

                timeout_count = 0
                acquired = False
                while not acquired and timeout_count <= 4:
                    acquired = lock.acquire(timeout=0.1)
                    if not acquired:
                        timeout_count += 1
                        logger.debug(f"Still waiting for worker {i} to finish...")
                
                if acquired:
                    lock.release()
                    logger.info(f"Worker {i} finished")
                else:
                    logger.warning(f"Worker {i} did not respond after 2 seconds, assuming it exited")


def single_worker_loop(_worker_id: int, lock, shutdown_event) -> None:
    shutdown_requested = False

    def signal_handler(signum, frame):
        nonlocal shutdown_requested
        logger.info(f"Worker {_worker_id} received signal: {signum}")
        shutdown_requested = True

        # Immediately requeue any active task
        current_frame = inspect.currentframe()
        try:
            while current_frame:
                if current_frame.f_code.co_name == "single_worker_loop":
                    local_vars = current_frame.f_locals
                    task_key = local_vars.get("task_key")
                    redis = local_vars.get("redis")
                    task = local_vars.get("task")

                    if task_key and redis and task:
                        logger.info(f"Worker {_worker_id} immediately requeuing task {task_key}")
                        try:
                            task_key_str = task_key.decode() if isinstance(task_key, bytes) else str(task_key)
                            parts = task_key_str.split(":", 2)
                            if len(parts) >= 3:
                                instance_id = parts[2]
                                result_key = f"result:{instance_id}:status"

                                redis.hset(result_key, "status", "pending")
                                redis.lpush("tasks", task_key_str)

                                logger.info(f"Worker {_worker_id} successfully requeued {task_key} immediately")
                            else:
                                logger.error(f"Could not parse instance_id from task_key: {task_key}")
                        except Exception as e:
                            logger.error(f"Failed to requeue task {task_key} in signal handler: {e}")
                    break
                current_frame = current_frame.f_back
        finally:
            if current_frame:
                del current_frame
        
        # Interrupt whatever is running since it is back to the queue
        logger.info(f"Worker {_worker_id} interrupting current task after requeuing")
        raise KeyboardInterrupt("Task requeued, interrupting execution")

    signal.signal(signal.SIGINT, signal_handler)

    redis = get_redis()

    task_key = None
    task = None

    try:
        while not shutdown_requested and not shutdown_event.is_set():
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
                if shutdown_requested or shutdown_event.is_set():
                    logger.info(f"Worker {_worker_id} shutdown requested - task {task_key} already requeued")
                    break

                run_task(task, str(task_key))

                task_key = None
                task = None
            else:
                logger.error(f"Failed to deserialize task data for {task_key=}")
                task_key = None

    except KeyboardInterrupt as e:
        logger.info(f"Worker {_worker_id} interrupted by signal (task was requeued): {e}")
    except Exception as e:
        logger.error(f"Worker {_worker_id} encountered error: {e}")
    finally:
        # Debug logging for task state
        shutdown_reason = []
        if shutdown_requested:
            shutdown_reason.append("signal")
        if shutdown_event.is_set():
            shutdown_reason.append("event")

        logger.info(f"Worker {_worker_id} exiting: shutdown_reason={shutdown_reason}")

        logger.info(f"Worker {_worker_id} acquiring lock to signal completion")
        lock.acquire()
        logger.info(f"Worker {_worker_id} has acquired lock and is exiting")


def run_task(task: TaskInstance, task_key: str) -> None:
    """
    Run a task to completion.
    """
    redis = get_redis()
    result_key = f"result:{task.instance_id}:status"

    redis.hset(result_key, "status", "running")

    args = task.args or []
    kwargs = task.kwargs or {}

    logger.info(f"running task {task.name=} {task.instance_id=}")

    try:
        result = task.callable(*args, **kwargs)
        logger.info(f"finished task {task.name=} {task.instance_id=}")
        redis.hset(result_key, "result", json.dumps(result))
        redis.hset(result_key, "status", "finished")
    except Exception as e:
        logger.info(f"failed task {task.name=} {task.instance_id=} with exception: {e}")
        redis.hset(result_key, "result", json.dumps({"error": str(e)}))
        redis.hset(result_key, "status", "failed")
