import itertools

from job_shop_lib.graphs import build_disjunctive_graph, EdgeType, NodeType


def test_disjunctive_edges_addition(example_job_shop_instance):
    graph = build_disjunctive_graph(example_job_shop_instance)
    for machine_operations in graph.nodes_by_machine:
        if len(machine_operations) <= 1:
            continue
        for node1, node2 in itertools.combinations(machine_operations, 2):
            assert (
                graph.graph.has_edge(node1, node2)
                and graph.graph[node1][node2]["type"] == EdgeType.DISJUNCTIVE
            )
            assert (
                graph.graph.has_edge(node2, node1)
                and graph.graph[node2][node1]["type"] == EdgeType.DISJUNCTIVE
            )


def test_conjunctive_edges_addition(example_job_shop_instance):
    graph = build_disjunctive_graph(example_job_shop_instance)
    for job_operations in graph.nodes_by_job:
        for i in range(1, len(job_operations)):
            assert (
                graph.graph.has_edge(job_operations[i - 1], job_operations[i])
                and graph.graph[job_operations[i - 1]][job_operations[i]][
                    "type"
                ]
                == EdgeType.CONJUNCTIVE
            )


def test_source_and_sink_nodes_addition(example_job_shop_instance):
    graph = build_disjunctive_graph(example_job_shop_instance)
    source_nodes = [
        node for node in graph.nodes if node.node_type == NodeType.SOURCE
    ]
    sink_nodes = [
        node for node in graph.nodes if node.node_type == NodeType.SINK
    ]
    assert len(source_nodes) == 1
    assert len(sink_nodes) == 1


def test_source_and_sink_edges_addition(example_job_shop_instance):
    graph = build_disjunctive_graph(example_job_shop_instance)
    source = next(
        node for node in graph.nodes if node.node_type == NodeType.SOURCE
    )
    sink = next(
        node for node in graph.nodes if node.node_type == NodeType.SINK
    )
    for job_operations in graph.nodes_by_job:
        assert (
            graph.graph.has_edge(source, job_operations[0])
            and graph.graph[source][job_operations[0]]["type"]
            == EdgeType.CONJUNCTIVE
        )
        assert (
            graph.graph.has_edge(job_operations[-1], sink)
            and graph.graph[job_operations[-1]][sink]["type"]
            == EdgeType.CONJUNCTIVE
        )
