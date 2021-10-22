from worker import worker

from services import run_agent


@worker.task
def a_plus_b(a, b):
    return a + b


@worker.task
def run_agent_task(agent_settings):
    run_agent(agent_settings)
