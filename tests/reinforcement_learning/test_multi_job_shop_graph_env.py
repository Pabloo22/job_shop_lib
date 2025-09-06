import random

import numpy as np

import pytest

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
    FeatureType,
)
from job_shop_lib.graphs import NodeType
from job_shop_lib.graphs.graph_updaters import ResidualGraphUpdater


def _random_action(observation: ObservationDict) -> tuple[int, int]:
    available_operations_with_ids = observation[
        ObservationSpaceKey.ACTION_MASK.value
    ]
    operation_id, machine_id, _ = random.choice(available_operations_with_ids)
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


@pytest.mark.skip
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


def test_observation(
    multi_job_shop_graph_env: MultiJobShopGraphEnv,
):
    """
    Tests the integrity of the observation space throughout a full episode.

    This test verifies that:
    1.  Edge indices in the observation correctly map to active nodes in the graph.
    2.  Node features for completed operations are properly zeroed out.
    3.  The number of node features matches the current number of nodes in the graph.
    4.  The episode concludes with a complete schedule and no available actions.
    """
    env = multi_job_shop_graph_env
    obs, _ = env.reset()
    done = False

    while not done:
        action = _random_action(obs)
        obs, _, done, *_ = env.step(action)

        # 1. Verify edge indices
        edge_index_dict = obs[ObservationSpaceKey.EDGE_INDEX.value]
        for edge_type, edges in edge_index_dict.items():
            assert edge_type in env.job_shop_graph.edge_types
            assert edges.ndim == 2 and edges.shape[0] == 2, (
                f"Edge index shape mismatch for {edge_type}: {edges.shape}"
            )
            # Ensure all node indices in edges are valid and point to active nodes
            src_nodes_type, _, dst_nodes_type = edge_type
            src_nodes, dst_nodes = edges

            # Calculate the maximum valid ID for source and destination node types
            src_type_removed_nodes = env.job_shop_graph.removed_nodes[src_nodes_type]
            dst_type_removed_nodes = env.job_shop_graph.removed_nodes[dst_nodes_type]
            max_src_id = len(src_type_removed_nodes) - sum(src_type_removed_nodes) - 1
            max_dst_id = len(dst_type_removed_nodes) - sum(dst_type_removed_nodes) - 1
            
            if edges.size > 0: # Only check if there are edges of this type
                assert np.all(src_nodes <= max_src_id), (
                    f"Source nodes {src_nodes} exceed max id {max_src_id} for type {src_nodes_type.name}"
                )
                assert np.all(dst_nodes <= max_dst_id), (
                    f"Destination nodes {dst_nodes} exceed max id {max_dst_id} for type {dst_nodes_type.name}"
                )

        # 2. Verify that features of completed operations are removed (sum to zero)
        op_features = obs[ObservationSpaceKey.NODE_FEATURES.value][FeatureType.OPERATIONS.value]
        op_completed_feats_sum = np.sum(op_features)
        assert op_completed_feats_sum == 0, (
            "Operation features are not correctly zeroed out for completed nodes. "
            f"Sum should be 0 but got {op_completed_feats_sum}"
        )

        # 3. Verify that the number of node features matches the number of active nodes
        assert op_features.shape[0] == len(env.job_shop_graph.nodes_by_type[NodeType.OPERATION]), (
            f"Operation features shape mismatch: {op_features.shape[0]} != "
            f"{len(env.job_shop_graph.nodes_by_type[NodeType.OPERATION])}"
        )

    # 4. Verify terminal state
    assert env.dispatcher.schedule.is_complete()
    assert len(obs[ObservationSpaceKey.ACTION_MASK.value]) == 0, (
        "Action mask should be empty at the end of the episode but is not. "
        f"Mask: {obs[ObservationSpaceKey.ACTION_MASK.value]}"
    )


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

    removed_nodes = multi_job_shop_graph_env.job_shop_graph.removed_nodes
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
