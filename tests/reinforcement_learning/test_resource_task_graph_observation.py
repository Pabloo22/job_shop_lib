import numpy as np
from job_shop_lib.reinforcement_learning import (
    SingleJobShopGraphEnv,
    ResourceTaskGraphObservation,
)


def test_edge_index_dict(
    single_env_ft06_resource_task_graph_with_all_features: (
        SingleJobShopGraphEnv
    ),
):
    env = ResourceTaskGraphObservation(
        single_env_ft06_resource_task_graph_with_all_features
    )
    obs, info = env.reset()
    max_index = env.unwrapped.job_shop_graph.instance.num_operations
    edge_index_dict = obs["edge_index_dict"]
    _check_that_edge_index_has_been_reindexed(edge_index_dict, max_index)

    done = False
    _, machine_id, job_id = info["available_operations_with_ids"][0]
    removed_nodes = env.unwrapped.job_shop_graph.removed_nodes
    _check_count_of_unique_ids(edge_index_dict, removed_nodes)
    while not done:
        obs, _, done, _, info = env.step((job_id, machine_id))
        if done:
            break
        edge_index_dict = obs["edge_index_dict"]
        _check_that_edge_index_has_been_reindexed(edge_index_dict, max_index)
        _, machine_id, job_id = info["available_operations_with_ids"][0]
        _check_count_of_unique_ids(edge_index_dict, removed_nodes)


def test_node_features_dict(
    single_env_ft06_resource_task_graph_with_all_features: (
        SingleJobShopGraphEnv
    ),
):
    env = ResourceTaskGraphObservation(
        single_env_ft06_resource_task_graph_with_all_features
    )
    obs, info = env.reset()
    done = False
    _, machine_id, job_id = info["available_operations_with_ids"][0]
    removed_nodes = env.unwrapped.job_shop_graph.removed_nodes
    _check_number_of_nodes(obs["node_features_dict"], removed_nodes)
    while not done:
        obs, _, done, _, info = env.step((job_id, machine_id))
        if done:
            break
        _check_number_of_nodes(obs["node_features_dict"], removed_nodes)
        _, machine_id, job_id = info["available_operations_with_ids"][0]


def test_original_ids_dict(
    single_env_ft06_resource_task_graph_with_all_features: (
        SingleJobShopGraphEnv
    ),
):
    env = ResourceTaskGraphObservation(
        single_env_ft06_resource_task_graph_with_all_features
    )
    obs, info = env.reset()
    done = False
    _, machine_id, job_id = info["available_operations_with_ids"][0]
    removed_nodes = env.unwrapped.job_shop_graph.removed_nodes
    _check_original_ids_dict(obs["original_ids_dict"], removed_nodes)
    while not done:
        obs, _, done, _, info = env.step((job_id, machine_id))
        if done:
            break
        _check_original_ids_dict(obs["original_ids_dict"], removed_nodes)
        _, machine_id, job_id = info["available_operations_with_ids"][0]


def test_type_ranges(
    single_env_ft06_resource_task_graph_with_all_features: (
        SingleJobShopGraphEnv
    ),
):
    env = ResourceTaskGraphObservation(
        single_env_ft06_resource_task_graph_with_all_features
    )
    assert "operation" in env.type_ranges
    assert "machine" in env.type_ranges
    # (it does not have job nodes)

    assert env.type_ranges["operation"] == (0, 36)
    assert env.type_ranges["machine"] == (36, 42)
    assert len(env.type_ranges) == 2


def _check_that_edge_index_has_been_reindexed(
    edge_index_dict: dict, max_idx: int
):
    for edge_index in edge_index_dict.values():
        assert np.all(edge_index >= 0)
        assert np.all(edge_index < max_idx)


def _check_count_of_unique_ids(
    edge_index_dict: dict[tuple[str, str, str], np.ndarray],
    removed_nodes: list[bool],
):
    number_of_alive_nodes = len(removed_nodes) - sum(removed_nodes)
    operation_nodes = np.zeros(36)
    machine_nodes = np.zeros(6)
    for key, edge_index in edge_index_dict.items():
        node_type1, _, node_type2 = key
        if node_type1 == "operation":
            operation_nodes[edge_index[0]] = 1
        elif node_type1 == "machine":
            machine_nodes[edge_index[0]] = 1
        if node_type2 == "operation":
            operation_nodes[edge_index[1]] = 1
        elif node_type2 == "machine":
            machine_nodes[edge_index[1]] = 1
    num_unique_ids = operation_nodes.sum() + machine_nodes.sum()
    assert num_unique_ids == number_of_alive_nodes


def _check_number_of_nodes(
    node_features_dict: dict[str, np.ndarray], removed_nodes: list[bool]
):
    number_of_alive_nodes = len(removed_nodes) - sum(removed_nodes)
    total_nodes = 0
    for node_features in node_features_dict.values():
        total_nodes += node_features.shape[0]
    assert total_nodes == number_of_alive_nodes


def _check_original_ids_dict(
    original_ids_dict: dict[str, np.ndarray], removed_nodes: list[bool]
):
    for node_type, original_ids in original_ids_dict.items():
        adjuster = 36 if node_type == "machine" else 0
        for original_id in original_ids:
            assert not removed_nodes[original_id + adjuster]


if __name__ == "__main__":
    import pytest

    pytest.main(["-v", __file__])
