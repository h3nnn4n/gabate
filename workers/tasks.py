from .services import run_agent
from .worker import worker


@worker.task
def a_plus_b(a, b):
    return a + b


@worker.task
def run_agent_task(agent_settings):
    return run_agent(agent_settings)


@worker.task
def evaluate_agent(agent_settings):
    return run_agent(agent_settings)
