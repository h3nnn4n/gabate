import json
from time import sleep

from queueer.task import TaskInstance, TaskSerializer
from utils import get_redis


def worker_loop() -> None:
    redis = get_redis()

    while True:
        print("waiting for task")
        task_key = redis.lpop("tasks")
        print(f"got task {task_key=}")


        if task_key is None:
            print("no task found")
            sleep(1)
            continue
            
        task_raw = redis.get(task_key)
        if task_raw is None:
            sleep(1)
            continue
            
        task = TaskSerializer.from_json(task_raw.decode())
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
    result = task.callable(*args, **kwargs)
    print(f"finished task {task.name=} {task.instance_id=}")
    
    redis.hset(result_key, "status", "finished")
    redis.hset(result_key, "result", json.dumps(result))