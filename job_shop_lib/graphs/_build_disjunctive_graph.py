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

from job_shop_lib import JobShopInstance, Schedule
from job_shop_lib.graphs import JobShopGraph, EdgeType, NodeType, Node


def build_disjunctive_graph(instance: JobShopInstance) -> JobShopGraph:
    """Builds and returns a disjunctive graph for the given job shop instance.

    This function creates a complete disjunctive graph from a
    :JobShopInstance.
    It starts by initializing a JobShopGraph object and proceeds by adding
    disjunctive edges between operations using the same machine, conjunctive
    edges between successive operations in the same job, and finally, special
    source and sink nodes with their respective edges to and from all other
    operations.

    Edges have a "type" attribute indicating whether they are disjunctive or
    conjunctive.

    Args:
        instance (JobShopInstance): The job shop instance for which to build
        the graph.

    Returns:
        A :class:`JobShopGraph` object representing the disjunctive graph
        of the job shop scheduling problem.
    """
    graph = JobShopGraph(instance)
    add_disjunctive_edges(graph)
    add_conjunctive_edges(graph)
    add_source_sink_nodes(graph)
    add_source_sink_edges(graph)
    return graph


def build_solved_disjunctive_graph(schedule: Schedule) -> JobShopGraph:
    """Builds and returns a disjunctive graph for the given solved schedule.

    This function constructs a disjunctive graph from the given schedule,
    keeping only the disjunctive edges that represent the chosen ordering
    of operations on each machine as per the solution schedule.

    Args:
        schedule (Schedule): The solved schedule that contains the sequencing
        of operations on each machine.

    Returns:
        A JobShopGraph object representing the disjunctive graph
        of the solved job shop scheduling problem.
    """
    # Build the base disjunctive graph from the job shop instance
    graph = JobShopGraph(schedule.instance)
    add_conjunctive_edges(graph)
    add_source_sink_nodes(graph)
    add_source_sink_edges(graph)

    # Iterate over each machine and add only the edges that match the solution
    # order
    for machine_schedule in schedule.schedule:
        for i, scheduled_operation in enumerate(machine_schedule):
            if i + 1 >= len(machine_schedule):
                break
            next_scheduled_operation = machine_schedule[i + 1]
            graph.add_edge(
                scheduled_operation.operation.operation_id,
                next_scheduled_operation.operation.operation_id,
                type=EdgeType.DISJUNCTIVE,
            )

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
