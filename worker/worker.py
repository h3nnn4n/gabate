from celery import Celery

worker = Celery("worker")

worker.config_from_object("celery_config")
