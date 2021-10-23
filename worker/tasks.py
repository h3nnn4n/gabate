from services import run_agent
from worker import worker


@worker.task
def a_plus_b(a, b):
    return a + b


@worker.task
def evaluate_agent(agent_settings):
    return run_agent(agent_settings)
