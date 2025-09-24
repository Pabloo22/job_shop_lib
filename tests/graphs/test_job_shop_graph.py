from collections import defaultdict
import pytest
import networkx as nx

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import (
    JobShopGraph,
    NodeType,
    add_conjunctive_edges,
    add_disjunctive_edges,
    add_source_sink_edges,
    add_source_sink_nodes,
    build_complete_resource_task_graph,
)


def test_initialization(example_job_shop_instance):
    graph = JobShopGraph(example_job_shop_instance)
    assert graph.instance is example_job_shop_instance
    assert len(graph.nodes) == graph.instance.num_operations


def test_nodes(example_job_shop_instance):
    graph = JobShopGraph(example_job_shop_instance)
    add_source_sink_nodes(graph)
    assert graph.nodes == [
        data["node"] for _, data in graph.graph.nodes(data=True)
    ]


def test_node_ids(example_job_shop_instance):
    """
    Tests that node IDs are correctly formatted tuples, that nodes can be
    retrieved by their ID, and that local IDs are sequential per type.
    """
    graph = JobShopGraph(example_job_shop_instance)
    add_source_sink_nodes(graph)

    nodes_by_type = defaultdict(list)

    # Part 1: Verify ID format and that the node is accessible by its ID
    for node in graph.nodes:
        node_id = node.node_id

        # Assert the ID is a tuple of (str, int)
        assert isinstance(node_id, tuple)
        assert len(node_id) == 2
        assert isinstance(node_id[0], str)
        assert isinstance(node_id[1], int)

        # Assert the node type in the ID matches the node's actual type
        assert node_id[0] == node.node_type.name.lower()

        # Assert that we can retrieve the exact same node using its ID
        # This tests the `nodes_map` functionality.
        assert graph.nodes_map[node_id] is node

        # Group nodes for the next part of the test
        nodes_by_type[node.node_type].append(node)

    # Part 2: Verify that local IDs are sequential for each type
    for _, nodes_of_that_type in nodes_by_type.items():
        # Extract the local_id (the integer) from each node's tuple ID
        local_ids = [node.node_id[1] for node in nodes_of_that_type]
        local_ids.sort()

        # Assert that the local IDs form a complete sequence from 0..N-1
        assert local_ids == list(range(len(nodes_of_that_type)))


def test_node_types(example_job_shop_instance):
    graph = JobShopGraph(example_job_shop_instance)
    assert all(node.node_type == NodeType.OPERATION for node in graph.nodes)
    add_source_sink_nodes(graph)
    assert all(
        node.node_type in (NodeType.OPERATION, NodeType.SOURCE, NodeType.SINK)
        for node in graph.nodes
    )


def test_nodes_by_type(example_job_shop_instance):
    graph = JobShopGraph(example_job_shop_instance)
    add_source_sink_nodes(graph)

    all_nodes = set()
    for nodes in graph.nodes_by_type.values():
        all_nodes.update(nodes)

    assert all_nodes == set(graph.nodes)


def test_nodes_by_machine(example_job_shop_instance):
    graph = JobShopGraph(example_job_shop_instance)

    # Intermediate operations to test against potential side effects
    add_source_sink_nodes(graph)
    add_conjunctive_edges(graph)
    add_disjunctive_edges(graph)
    add_source_sink_edges(graph)

    for machine_id, nodes in enumerate(graph.nodes_by_machine):
        assert all(node.operation.machine_id == machine_id for node in nodes)


def test_nodes_by_job(example_job_shop_instance):
    graph = JobShopGraph(example_job_shop_instance)

    # Intermediate operations to test against potential side effects
    add_source_sink_nodes(graph)
    add_conjunctive_edges(graph)
    add_disjunctive_edges(graph)
    add_source_sink_edges(graph)

    for job_id, nodes in enumerate(graph.nodes_by_job):
        assert all(node.operation.job_id == job_id for node in nodes)


def test_operation_nodes_addition(example_job_shop_instance):
    graph = JobShopGraph(example_job_shop_instance)
    operation_nodes = [
        node for node in graph.nodes if node.node_type == NodeType.OPERATION
    ]
    assert len(operation_nodes) == sum(
        len(job) for job in example_job_shop_instance.jobs
    )


def test_remove_node(example_job_shop_instance):
    graph = JobShopGraph(example_job_shop_instance)
    # Initially add some nodes to the graph
    add_source_sink_nodes(graph)
    add_conjunctive_edges(graph)
    add_disjunctive_edges(graph)
    add_source_sink_edges(graph)
    # Dynamically select valid tuple IDs to remove.
    # This is more robust than hardcoding integer indices.
    op_nodes = graph.nodes_by_type[NodeType.OPERATION]
    # Ensure there are enough nodes to run the test
    assert len(op_nodes) >= 7, "Test instance needs at least 7 operations"
    nodes_to_remove = [
        op_nodes[0],
        op_nodes[3],
        op_nodes[6],
    ]

    # Remove nodes using their correct tuple IDs
    for node in nodes_to_remove:
        graph.remove_node(node.node_id)

    # Verify the nodes are no longer in the graph's node set
    for node in nodes_to_remove:
        if node.node_id in graph.nodes_map:
            assert (
                graph.nodes_map[node.node_id].operation.operation_id
                != node.operation.operation_id
            )

    # Verify the `removed_nodes` attribute is updated correctly via the API
    for node in nodes_to_remove:
        assert graph.is_removed(node)

    with pytest.raises(nx.NetworkXError):
        # Seeing all edges of removed nodes just returns an empty list, not an error
        # So we try to access an edge that should not exist
        last_removed_node_id = nodes_to_remove[-1]
        graph.graph.remove_edge(last_removed_node_id, ("SOURCE", 0))

    # This part of the test remains valid as it uses the is_removed() helper
    graph.remove_isolated_nodes()
    isolated_nodes = list(nx.isolates(graph.graph))
    assert not isolated_nodes

    # Verify the integrity of the remaining graph structure
    remaining_node_ids = {
        node.node_id for node in graph.nodes if not graph.is_removed(node)
    }
    for u, v in graph.graph.edges():
        assert u in remaining_node_ids
        assert v in remaining_node_ids


def test_get_machine_node(example_job_shop_instance: JobShopInstance):
    graph = build_complete_resource_task_graph(example_job_shop_instance)

    for machine_id in range(example_job_shop_instance.num_machines):
        machine_node = graph.get_machine_node(machine_id)
        assert machine_node.node_type == NodeType.MACHINE
        assert machine_node.machine_id == machine_id


def test_get_job_node(example_job_shop_instance: JobShopInstance):
    graph = build_complete_resource_task_graph(example_job_shop_instance)

    for job_id in range(example_job_shop_instance.num_jobs):
        job_node = graph.get_job_node(job_id)
        assert job_node.node_type == NodeType.JOB
        assert job_node.job_id == job_id


def test_get_operation_node(example_job_shop_instance: JobShopInstance):
    graph = build_complete_resource_task_graph(example_job_shop_instance)

    for job in example_job_shop_instance.jobs:
        for operation in job:
            operation_node = graph.get_operation_node(operation.operation_id)
            assert operation_node.node_type == NodeType.OPERATION
            assert (
                operation_node.operation.operation_id == operation.operation_id
            )


if __name__ == "__main__":
    pytest.main(["-vv", "tests/graphs/test_job_shop_graph.py"])
