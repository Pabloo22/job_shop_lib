"""Module for building the disjunctive graph of a job shop instance.

The disjunctive graph is created by first adding nodes representing each
operation in the jobs, along with two special nodes: a source $S$ and a sink
$T$. Each operation node is linked to the next operation in its job sequence
by **conjunctive edges**, forming a path from the source to the sink. These
edges represent the order in which operations of a single job must be
performed.

Additionally, the graph includes **disjunctive edges** between operations
that use the same machine but belong to different jobs. These edges are
bidirectional, indicating that either of the connected operations can be
performed first. The disjunctive edges thus represent the scheduling choices
available: the order in which operations sharing a machine can be processed.
Solving the Job Shop Scheduling problem involves choosing a direction for
each disjunctive edge such that the overall processing time is minimized.
"""

import itertools

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import JobShopGraph, EdgeType, NodeType, Node


def build_disjunctive_graph(instance: JobShopInstance) -> JobShopGraph:
    graph = JobShopGraph(instance)
    add_disjunctive_edges(graph)
    add_conjunctive_edges(graph)
    add_source_sink_nodes(graph)
    add_source_sink_edges(graph)
    return graph


def add_disjunctive_edges(graph: JobShopGraph) -> None:
    """Adds disjunctive edges to the graph."""

    for machine in graph.nodes_by_machine:
        for node1, node2 in itertools.combinations(machine, 2):
            graph.add_edge(
                node1,
                node2,
                type=EdgeType.DISJUNCTIVE,
            )
            graph.add_edge(
                node2,
                node1,
                type=EdgeType.DISJUNCTIVE,
            )


def add_conjunctive_edges(graph: JobShopGraph) -> None:
    """Adds conjunctive edges to the graph."""

    for job_operations in graph.nodes_by_job:
        for i in range(1, len(job_operations)):
            graph.add_edge(
                job_operations[i - 1],
                job_operations[i],
                type=EdgeType.CONJUNCTIVE,
            )


def add_source_sink_nodes(graph: JobShopGraph) -> None:
    """Adds source and sink nodes to the graph."""
    source = Node(node_type=NodeType.SOURCE)
    sink = Node(node_type=NodeType.SINK)
    graph.add_node(source)
    graph.add_node(sink)


def add_source_sink_edges(graph: JobShopGraph) -> None:
    """Adds edges between source and sink nodes and operations."""
    source = graph.nodes_by_type[NodeType.SOURCE][0]
    sink = graph.nodes_by_type[NodeType.SINK][0]

    for job_operations in graph.nodes_by_job:
        graph.add_edge(source, job_operations[0], type=EdgeType.CONJUNCTIVE)
        graph.add_edge(job_operations[-1], sink, type=EdgeType.CONJUNCTIVE)
