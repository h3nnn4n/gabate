from ..agent import Agent


def test_to_json():
    agent = Agent()
    data = agent.get_agent_data()

    for weight in data["agent"]["weights"]:
        assert -5 <= weight and weight <= 5
