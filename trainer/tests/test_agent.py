from mock import patch

from ..agent import Agent


def test_to_json():
    agent = Agent()
    data = agent.get_agent_data()

    for weight in data["agent"]["weights"]:
        assert -5 <= weight and weight <= 5


def test_clone_weights():
    agent = Agent()
    new_agent = agent.clone()

    assert len(agent.settings["weights"]) == len(new_agent.settings["weights"])
    assert agent.settings["weights"] == new_agent.settings["weights"]


def test_clone_dirty():
    agent = Agent()
    new_agent = agent.clone()

    assert agent._dirty_fitness == new_agent._dirty_fitness
    assert new_agent._dirty_fitness


def test_clone_non_dirty():
    agent = Agent()
    with patch.object(agent, "_get_scores", return_value=[1, 2, 3]):
        agent.get_fitness()

    new_agent = agent.clone()

    assert agent._dirty_fitness == new_agent._dirty_fitness
    assert not new_agent._dirty_fitness


def test_fitness():
    agent = Agent()
    with patch.object(agent, "_get_scores", return_value=[1, 2, 3]):
        scores = agent.get_fitness()

    assert "min" in scores.keys()
    assert "median" in scores.keys()
    assert "max" in scores.keys()
    assert "raw" in scores.keys()

    assert scores["min"] == 1
    assert scores["median"] == 2
    assert scores["max"] == 3
    assert scores["raw"] == [1, 2, 3]
