import dramatiq


@dramatiq.actor(store_results=True)
def a_plus_b(a, b):
    pass


@dramatiq.actor(store_results=True, time_limit=1000 * 60 * 60 * 24 * 7)
def evaluate_agent(agent_settings):
    pass
