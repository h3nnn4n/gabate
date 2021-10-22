import os

from dotenv import load_dotenv


load_dotenv()

broker_url = os.environ.get("BROKER_URL", "pyamqp://guest@localhost")
result_backend = os.environ.get("RESULT_BACKEND", "redis://localhost")

task_acks_late = True
worker_prefetch_multiplier = 1

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "America/Sao_Paulo"
enable_utc = True
