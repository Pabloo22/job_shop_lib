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
