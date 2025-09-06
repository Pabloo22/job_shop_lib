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
    return (operation_id, machine_id)

def debug_observation(obs, space):
    """Prints a detailed comparison of an observation and its space."""
    print("--- STARTING OBSERVATION DEBUG ---")

    # 1. Top-Level Key Check
    obs_keys = set(obs.keys())
    space_keys = set(space.keys())
    if obs_keys != space_keys:
        print(f"❌ MISMATCH: Top-level keys do not match!")
        print(f"   Obs Keys:   {sorted(list(obs_keys))}")
        print(f"   Space Keys: {sorted(list(space_keys))}")
        # Find differences
        print(f"   Missing in Obs:   {space_keys - obs_keys}")
        print(f"   Extra in Obs:     {obs_keys - space_keys}")
        return

    print("✅ Top-level keys match.")

    # 2. Check Each Component
    for key, obs_value in obs.items():
        sub_space = space[key]
        print(f"\n--- Checking Component: '{key}' ---")

        # Handle Dict spaces (like NODE_FEATURES and EDGE_INDEX)
        if isinstance(sub_space, gym.spaces.Dict):
            obs_sub_keys = set(obs_value.keys())
            space_sub_keys = set(sub_space.keys())
            if obs_sub_keys != space_sub_keys:
                print(f"❌ MISMATCH: Keys inside '{key}' do not match!")
                print(f"   Obs Keys:   {sorted(list(obs_sub_keys))}")
                print(f"   Space Keys: {sorted(list(space_sub_keys))}")
                continue

            print(f"✅ Keys inside '{key}' match.")
            # Check each array in the Dict
            for sub_key, array in obs_value.items():
                array_space = sub_space[sub_key]
                if not array_space.contains(array):
                    print(f"❌ MISMATCH: Array '{key}':'{sub_key}' is invalid!")
                    print(f"   Obs Shape: {array.shape}, Space Shape: {array_space.shape}")
                    print(f"   Obs Dtype: {array.dtype}, Space Dtype: {array_space.dtype}")
                    if array.shape != array_space.shape:
                        print("   Reason: SHAPE MISMATCH")
                    elif array.dtype != array_space.dtype:
                        print("   Reason: DTYPE MISMATCH")
                    else:
                        print("   Reason: VALUE OUT OF BOUNDS")
                else:
                    print(f"✅ Array '{key}':'{sub_key}' is valid.")

        # Handle Sequence spaces (like ACTION_MASK)
        elif isinstance(sub_space, gym.spaces.Sequence):
            if not isinstance(obs_value, (list, tuple)):
                print(f"❌ MISMATCH: '{key}' should be a list or tuple, but got {type(obs_value)}")
                continue

            print(f"✅ Component '{key}' is a list/tuple.")
            if len(obs_value) > 0:
                # Check the type of the first element
                first_elem = obs_value[0]
                if not isinstance(first_elem, np.ndarray):
                     print(f"❌ MISMATCH: Elements in '{key}' should be np.ndarray, but found {type(first_elem)}")
                     continue
                print(f"✅ Elements in '{key}' are of type np.ndarray.")

                # Check each element in the sequence
                for i, elem in enumerate(obs_value):
                    if not sub_space.feature_space.contains(elem):
                        print(f"❌ MISMATCH: Element {i} in '{key}' is invalid!")
                        elem_space = sub_space.feature_space
                        print(f"   Obs Shape: {elem.shape}, Space Shape: {elem_space.shape}")
                        print(f"   Obs Dtype: {elem.dtype}, Space Dtype: {elem_space.dtype}")
                        print(f"   Obs Value: {elem}")
                        break
                else:
                    print(f"✅ All elements in '{key}' are valid.")
            else:
                print("✅ Component '{key}' is an empty list, which is valid.")
    print("\n--- DEBUGGING COMPLETE ---")

def test_observation_space(
    single_job_shop_graph_env_ft06: SingleJobShopGraphEnv,
):
    env = single_job_shop_graph_env_ft06
    observation_space = single_job_shop_graph_env_ft06.observation_space
    num_edges = env.initial_job_shop_graph.num_edges
    edge_index_shape = [2, 0]
    for _, space in list(
        observation_space[ObservationSpaceKey.EDGE_INDEX].spaces.items()
    ):
        edge_index_shape[1] += space.shape[1]
    assert tuple(edge_index_shape) == (2, num_edges)

    done = False
    obs, _ = env.reset()
    debug_observation(obs, observation_space)
    assert observation_space.contains(obs), obs
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
            assert edges.ndim == 2 and edges.shape[0] == 2, \
                f"Edge index shape mismatch for {edge_type}: {edges.shape}"
            src_nodes_type, _, dst_nodes_type = edge_type
            src_nodes, dst_nodes = edges
            src_type_removed_nodes = env.job_shop_graph.removed_nodes[src_nodes_type]
            dst_type_removed_nodes = env.job_shop_graph.removed_nodes[dst_nodes_type]
            max_src_id = len(src_type_removed_nodes) - sum(src_type_removed_nodes) - 1
            max_dst_id = len(dst_type_removed_nodes) - sum(dst_type_removed_nodes) - 1
            assert np.all(src_nodes <= max_src_id), f"Source nodes {src_nodes} exceed max id {max_src_id}"
            assert np.all(dst_nodes <= max_dst_id), f"Destination nodes {dst_nodes} exceed max id {max_dst_id}"
        # Using is_completed features for operations, to see features of removed operation nodes are removed
        # We sum the operation features, if sum is equal to 0 always, means it is correctly
        # removing completed operation nodes from the graph, thus returning correct node_features_dict
        op_completed_feats_sum = np.sum(obs[ObservationSpaceKey.NODE_FEATURES.value][FeatureType.OPERATIONS.value])
        assert op_completed_feats_sum == 0, \
            f"Operation features are not correctly removed, sum should be 0 but got {op_completed_feats_sum}"
        assert obs[ObservationSpaceKey.NODE_FEATURES.value][FeatureType.OPERATIONS.value].shape[0]  \
        == len(env.job_shop_graph.nodes_by_type[NodeType.OPERATION]), \
        f"Operation features shape mismatch: {obs[ObservationSpaceKey.NODE_FEATURES.value][FeatureType.OPERATIONS.value].shape[0]} != {len(env.job_shop_graph.nodes_by_type[NodeType.OPERATION])}"


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
