import random

import pytest

import gymnasium as gym

import numpy as np

from job_shop_lib.reinforcement_learning import (
    SingleJobShopGraphEnv,
    ObservationSpaceKey,
    ObservationDict,
)


def random_action(observation: ObservationDict) -> tuple[int, int]:
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

@pytest.mark.skip
def test_observation_space(
    single_job_shop_graph_env_ft06: SingleJobShopGraphEnv,
):
    env = single_job_shop_graph_env_ft06
    observation_space = single_job_shop_graph_env_ft06.observation_space
    num_edges = env.job_shop_graph.num_edges
    edge_index_shape = [2, 0]

    if env.use_padding:
        i = 0
        for _, space in list(
            observation_space[ObservationSpaceKey.EDGE_INDEX].spaces.items()
        ):
            edge_index_shape[1] += space.shape[1]
            i += 1
        assert tuple(edge_index_shape) == (2, num_edges * i)
    else:
        for _, space in list(
            observation_space[ObservationSpaceKey.EDGE_INDEX].spaces.items()
        ):
            edge_index_shape[1] += space.shape[1]
        assert tuple(edge_index_shape) == (2, env.job_shop_graph.num_edges)

    done = False
    obs, _ = env.reset()
    assert observation_space.contains(obs)
    while not done:
        action = random_action(obs)
        obs, _, done, *_ = env.step(action)
        assert observation_space.contains(obs)

    env.use_padding = False
    done = False
    obs, _ = env.reset()
    edge_index_has_changed = False

    while not done:
        action = random_action(obs)
        obs, _, done, *_ = env.step(action)
        edge_index = obs[ObservationSpaceKey.EDGE_INDEX.value]
        shape = [2, 0]
        for edge in edge_index.values():
            shape[1] += edge.shape[1]
        if tuple(shape) != edge_index_shape:
            edge_index_has_changed = True
            break
    assert edge_index_has_changed


@pytest.mark.skip
def test_edge_index_padding(
    single_job_shop_graph_env_ft06: SingleJobShopGraphEnv,
):
    env = single_job_shop_graph_env_ft06

    done = False
    obs, _ = env.reset()
    while not done:
        action = random_action(obs)
        obs, _, done, *_ = env.step(action)

        edge_index = obs[ObservationSpaceKey.EDGE_INDEX.value]
        edges = env.observation_space[  # type: ignore[index]
            ObservationSpaceKey.EDGE_INDEX.value
        ].shape[1]
        assert edge_index.shape == (2, edges)

        padding_mask = edge_index == -1
        if np.any(padding_mask):
            # Ensure all padding is at the end
            for row in padding_mask:
                padding_start = np.argmax(row)
                if padding_start > 0:
                    assert np.all(row[padding_start:])

    assert env.dispatcher.schedule.is_complete()
    try:
        assert np.all(obs[ObservationSpaceKey.REMOVED_NODES.value])
    except AssertionError:
        print(obs[ObservationSpaceKey.REMOVED_NODES.value])
        print(env.instance.to_dict())
        print(env.instance)
        print(env.job_shop_graph.nodes)
        raise


def test_all_nodes_removed(
    single_job_shop_graph_env_ft06_resource_task: SingleJobShopGraphEnv,
):
    env = single_job_shop_graph_env_ft06_resource_task
    obs, _ = env.reset()
    done = False
    while not done:
        action = random_action(obs)
        obs, _, done, *_ = env.step(action)

    assert env.dispatcher.schedule.is_complete()
    removed_nodes = env.job_shop_graph.removed_nodes

    assert env.job_shop_graph is env.graph_updater.job_shop_graph
    try:
        print(removed_nodes)
        print(removed_nodes.values())
        print([all(value) for value in removed_nodes.values()])
        assert all(all(value) for value in removed_nodes.values())
    except AssertionError:
        print(removed_nodes)
        print(env.instance.to_dict())
        print(env.instance)
        print(env.job_shop_graph.nodes)
        raise


if __name__ == "__main__":
    import pytest

    pytest.main(["-vv", __file__])
