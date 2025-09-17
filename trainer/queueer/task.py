import json
import logging
import typing as t
from dataclasses import dataclass

from .utils import get_redis

logger = logging.getLogger(__name__)


class TaskNotFinishedError(Exception):
    pass


class TaskFailedError(Exception):
    pass


class TaskSerializer:
    """Handles JSON serialization and deserialization of Task instances."""

    @staticmethod
    def to_json(task_instance: "TaskInstance") -> str:
        """Convert TaskInstance to JSON string."""
        # Create a dict without the callable since it can't be serialized
        data = {
            "name": task_instance.name,
            "instance_id": task_instance.instance_id,
            "args": task_instance.args,
            "kwargs": task_instance.kwargs,
        }
        return json.dumps(data)

    @staticmethod
    def from_json(json_str: str) -> "TaskInstance":
        """Create TaskInstance from JSON string."""
        data = json.loads(json_str)
        # We can't restore the callable from JSON, so we'll need to get it from tasks module
        from tasks import get_task_by_name

        callable_func = get_task_by_name(data["name"]).callable
        return TaskInstance(
            name=data["name"],
            callable=callable_func,
            instance_id=data["instance_id"],
            args=data.get("args"),
            kwargs=data.get("kwargs"),
        )


@dataclass
class Task:
    name: str
    callable: t.Callable[..., t.Any]


@dataclass
class TaskInstance(Task):
    instance_id: str
    args: t.Optional[list] = None
    kwargs: t.Optional[dict] = None

    def get_result(self) -> t.Any:
        redis = get_redis()
        result_key = f"result:{self.instance_id}:status"

        task_status_raw = redis.hget(result_key, "status")
        if task_status_raw is None:
            raise TaskNotFinishedError(f"Task {self.instance_id} not found")

        task_status = task_status_raw.decode() if isinstance(task_status_raw, bytes) else task_status_raw
        finished = task_status == "finished"
        failed = task_status == "failed"

        if failed:
            raise TaskFailedError(f"Task {self.instance_id} failed")

        if not finished:
            raise TaskNotFinishedError(f"Task {self.instance_id} is not finished")

        result_raw = redis.hget(result_key, "result")

        if result_raw is None:
            return None

        result = json.loads(result_raw.decode() if isinstance(result_raw, bytes) else str(result_raw))
        return result


@dataclass
class TaskResult:
    task_id: str
    result: t.Any
    status: str = "pending"


def send_task(task: Task, task_id: str, args: t.Optional[list] = None, kwargs: t.Optional[dict] = None):
    task_instance = TaskInstance(
        instance_id=task_id,
        name=task.name,
        callable=task.callable,
        args=args,
        kwargs=kwargs,
    )

    logger.debug(f"sent task {task_instance.name=} {task_instance.instance_id=}")
    redis = get_redis()
    task_key = f"task:{task_instance.name}:{task_instance.instance_id}"
    payload = TaskSerializer.to_json(task_instance)
    redis.set(task_key, payload)
    redis.lpush(f"tasks", task_key)

    return task_instance
