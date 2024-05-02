import pytest
import networkx as nx

from job_shop_lib.graphs import (
    JobShopGraph,
    NodeType,
    add_conjunctive_edges,
    add_disjunctive_edges,
    add_source_sink_edges,
    add_source_sink_nodes,
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
    graph = JobShopGraph(example_job_shop_instance)
    add_source_sink_nodes(graph)

    # We don't use enumerate here because we want to test if we can
    # access the node by its id
    for i in range(graph.graph.number_of_nodes()):
        assert graph.nodes[i].node_id == i


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

    # Assumption: graph initially has nodes to remove
    node_to_remove = graph.nodes[0].node_id

    nodes_to_remove = [0, 3, 6]

    for node_id in nodes_to_remove:
        graph.remove_node(node_id)

    # Verify the node is no longer in the graph
    for node_to_remove in nodes_to_remove:
        assert node_to_remove not in graph.graph.nodes()

    # Verify isolated nodes are also removed and that the source node has
    # been removed due to the removal of the isolated nodes
    isolated_nodes = list(nx.isolates(graph.graph))
    assert not isolated_nodes
    source_node = graph.nodes_by_type[NodeType.SOURCE][0]
    assert graph.is_removed(source_node)

    # Verify the `removed_nodes` list is updated correctly
    for node_to_remove in nodes_to_remove:
        assert graph.removed_nodes[node_to_remove]

    # Optional: Check that no edges remain that involve the removed node
    with pytest.raises(nx.NetworkXError):
        graph.graph.edges(node_to_remove)

    # Check the integrity of the remaining graph structure
    remaining_node_ids = {
        node.node_id for node in graph.nodes if not graph.is_removed(node)
    }
    for u, v in graph.graph.edges():
        assert u in remaining_node_ids
        assert v in remaining_node_ids


if __name__ == "__main__":
    pytest.main(["-v", "tests/graphs/test_job_shop_graph.py"])
