import dramatiq

from services import run_agent


@dramatiq.actor(store_results=True)
def a_plus_b(a, b):
    return a + b


@dramatiq.actor(store_results=True)
def evaluate_agent(agent_settings):
    return run_agent(agent_settings)
