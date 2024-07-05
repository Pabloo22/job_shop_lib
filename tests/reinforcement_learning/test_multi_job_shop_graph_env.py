import random

import numpy as np

from job_shop_lib.reinforcement_learning import (
    MultiJobShopGraphEnv,
    ObservationSpaceKey,
    ObservationDict,
    MakespanReward,
)
from job_shop_lib.dispatching import Dispatcher, DispatcherObserver
from job_shop_lib.dispatching.feature_observers import (
    CompositeFeatureObserver,
    IsCompletedObserver,
)
from job_shop_lib.graphs.graph_updaters import ResidualGraphUpdater


def _random_action(observation: ObservationDict) -> tuple[int, int]:
    ready_operations = []
    for operation_id, is_ready in enumerate(
        observation[ObservationSpaceKey.JOBS.value].ravel()
    ):
        if is_ready == 1.0:
            ready_operations.append(operation_id)

    operation_id = random.choice(ready_operations)
    machine_id = -1  # We can use -1 if each operation can only be scheduled
    # in one machine.
    return (operation_id, machine_id)


def test_consistent_observation_space(
    multi_job_shop_graph_env: MultiJobShopGraphEnv,
):
    """Tests that the observation space is consistent across multiple
    resets."""

    env = multi_job_shop_graph_env
    observation_space = multi_job_shop_graph_env.observation_space

    for _ in range(100):
        _ = env.reset()
        assert observation_space == env.observation_space


def test_observation_space(
    multi_job_shop_graph_env: MultiJobShopGraphEnv,
):
    random.seed(42)

    env = multi_job_shop_graph_env
    observation_space = multi_job_shop_graph_env.observation_space
    edge_index_shape = observation_space[
        ObservationSpaceKey.EDGE_INDEX.value
    ].shape
    for _ in range(100):
        done = False
        obs, _ = env.reset()
        assert observation_space.contains(obs)
        while not done:
            action = _random_action(obs)
            obs, _, done, *_ = env.step(action)
            assert observation_space.contains(obs)

    env.use_padding = False
    done = False
    obs, _ = env.reset()
    edge_index_has_changed = False
    while not done:
        action = _random_action(obs)
        obs, _, done, *_ = env.step(action)
        edge_index = obs[ObservationSpaceKey.EDGE_INDEX.value]
        if edge_index.shape != edge_index_shape:
            edge_index_has_changed = True
            break
    assert edge_index_has_changed


def test_edge_index_padding(
    multi_job_shop_graph_env: MultiJobShopGraphEnv,
):
    random.seed(100)
    env = multi_job_shop_graph_env

    for _ in range(1):
        done = False
        obs, _ = env.reset()
        while not done:
            action = _random_action(obs)
            obs, _, done, *_ = env.step(action)

            edge_index = obs[ObservationSpaceKey.EDGE_INDEX.value]
            num_edges = env.observation_space[  # type: ignore[index]
                ObservationSpaceKey.EDGE_INDEX.value
            ].shape[1]
            assert edge_index.shape == (2, num_edges)

            padding_mask = edge_index == -1
            if np.any(padding_mask):
                # Ensure all padding is at the end
                for row in padding_mask:
                    padding_start = np.argmax(row)
                    if padding_start > 0:
                        assert np.all(row[padding_start:])


def test_all_nodes_are_removed(
    multi_job_shop_graph_env: MultiJobShopGraphEnv,
) -> None:
    env = multi_job_shop_graph_env
    for _ in range(1):
        obs, _ = env.reset()
        done = False
        while not done:
            action = _random_action(obs)
            obs, _, done, *_ = env.step(action)

    removed_nodes = obs[ObservationSpaceKey.REMOVED_NODES.value]
    try:
        assert np.all(removed_nodes)
    except AssertionError:
        print(removed_nodes)
        print(env.instance.to_dict())
        print(env.instance)
        print(env.job_shop_graph.nodes)
        raise


def test_reset(
    multi_job_shop_graph_env: MultiJobShopGraphEnv,
):
    env = multi_job_shop_graph_env
    env.reset()
    dispatcher = env.dispatcher
    assert env.dispatcher.current_time() == 0
    assert env.dispatcher.completed_operations() == set()
    env.reset()
    new_dispatcher = env.dispatcher
    assert dispatcher is not new_dispatcher

    expected_observers: list[type[DispatcherObserver]] = [
        IsCompletedObserver,
        CompositeFeatureObserver,
        ResidualGraphUpdater,
        MakespanReward,
    ]
    for observer_type in expected_observers:
        assert _is_observer_in_dispatcher(new_dispatcher, observer_type)


def _is_observer_in_dispatcher(
    dispatcher: Dispatcher, observer_type: type[DispatcherObserver]
) -> bool:
    for observer in dispatcher.subscribers:
        if isinstance(observer, observer_type):
            return True
    return False


if __name__ == "__main__":
    import pytest

    pytest.main(["-vv", __file__])
