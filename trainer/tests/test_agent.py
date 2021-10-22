import json

from ..agent import Agent


def test_to_json():
    agent = Agent()
    raw_json = agent.to_json()
    data = json.loads(raw_json)

    for weight in data["agent"]["weights"]:
        assert -5 <= weight and weight <= 5
