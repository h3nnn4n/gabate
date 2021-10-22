from random import random
from time import sleep

from worker import worker


@worker.task
def add(x, y):
    sleep(random() * 2)
    return x + y
