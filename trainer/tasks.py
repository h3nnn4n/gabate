import dramatiq


@dramatiq.actor(store_results=True)
def a_plus_b(a, b):
    pass


@dramatiq.actor(store_results=True)
def evaluate_agent(agent_settings):
    pass
