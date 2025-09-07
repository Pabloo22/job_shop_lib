import random

import pytest

import gymnasium as gym

import numpy as np


from job_shop_lib.reinforcement_learning import (
    SingleJobShopGraphEnv,
    ObservationSpaceKey,
    ObservationDict,
    add_padding,
)

from job_shop_lib.dispatching.feature_observers import (
    FeatureType,
)

from job_shop_lib.graphs import NodeType


def random_action(observation: ObservationDict) -> tuple[int, int]:
    available_operations_with_ids = observation[
        ObservationSpaceKey.ACTION_MASK.value
    ]
    operation_id, machine_id, _ = random.choice(available_operations_with_ids)
    return (int(operation_id), int(machine_id))


def test_observation_space(
    single_job_shop_graph_env_ft06: SingleJobShopGraphEnv,
):
    env = single_job_shop_graph_env_ft06
    observation_space = env.observation_space
    num_edges = env.initial_job_shop_graph.num_edges
    edge_index_shape = [2, 0]
    for _, space in list(
        observation_space[ObservationSpaceKey.EDGE_INDEX].spaces.items()
    ):
        edge_index_shape[1] += space.shape[1]
    assert tuple(edge_index_shape) == (2, num_edges)

    done = False
    obs, _ = env.reset()
    assert observation_space.contains(obs)
    while not done:
        action = random_action(obs)
        obs, _, done, *_ = env.step(action)
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


def test_observation(
    single_job_shop_graph_env_ft06: SingleJobShopGraphEnv,
):
    env = single_job_shop_graph_env_ft06

    done = False
    obs, _ = env.reset()
    while not done:
        action = random_action(obs)
        obs, _, done, *_ = env.step(action)

        edge_index = obs[ObservationSpaceKey.EDGE_INDEX.value]

        for edge_type, edges in edge_index.items():
            assert edge_type in env.job_shop_graph.edge_types
            assert (
                edges.ndim == 2 and edges.shape[0] == 2
            ), f"Edge index shape mismatch for {edge_type}: {edges.shape}"
            src_nodes_type, _, dst_nodes_type = edge_type
            src_nodes, dst_nodes = edges
            src_type_removed_nodes = env.job_shop_graph.removed_nodes[
                src_nodes_type
            ]
            dst_type_removed_nodes = env.job_shop_graph.removed_nodes[
                dst_nodes_type
            ]
            max_src_id = (
                len(src_type_removed_nodes) - sum(src_type_removed_nodes) - 1
            )
            max_dst_id = (
                len(dst_type_removed_nodes) - sum(dst_type_removed_nodes) - 1
            )
            assert np.all(
                src_nodes <= max_src_id
            ), f"Source nodes {src_nodes} exceed max id {max_src_id}"
            assert np.all(
                dst_nodes <= max_dst_id
            ), f"Destination nodes {dst_nodes} exceed max id {max_dst_id}"
        # Using is_completed features for operations, to see features of removed operation nodes are removed
        # We sum the operation features, if sum is equal to 0 always, means it is correctly
        # removing completed operation nodes from the graph, thus returning correct node_features_dict
        op_completed_feats_sum = np.sum(
            obs[ObservationSpaceKey.NODE_FEATURES.value][
                FeatureType.OPERATIONS.value
            ]
        )
        assert (
            op_completed_feats_sum == 0
        ), f"Operation features are not correctly removed, sum should be 0 but got {op_completed_feats_sum}"
        assert obs[ObservationSpaceKey.NODE_FEATURES.value][
            FeatureType.OPERATIONS.value
        ].shape[0] == len(
            env.job_shop_graph.nodes_by_type[NodeType.OPERATION]
        ), f"Operation features shape mismatch: {obs[ObservationSpaceKey.NODE_FEATURES.value][FeatureType.OPERATIONS.value].shape[0]} != {len(env.job_shop_graph.nodes_by_type[NodeType.OPERATION])}"

    assert env.dispatcher.schedule.is_complete()
    try:
        assert len(obs[ObservationSpaceKey.ACTION_MASK.value]) == 0
    except AssertionError:
        print("Action mask is not empty but schedule is complete:")
        print(obs[ObservationSpaceKey.ACTION_MASK.value])
        raise


def test_all_nodes_removed(
    single_job_shop_graph_env_ft06_resource_task: SingleJobShopGraphEnv,
):
    env = single_job_shop_graph_env_ft06_resource_task
    obs, _ = env.reset()
    done = False
    print("Initial observation:")
    print(obs)

    while not done:
        action = random_action(obs)
        obs, _, done, _, info = env.step(action)  # type: ignore[call-arg]

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
