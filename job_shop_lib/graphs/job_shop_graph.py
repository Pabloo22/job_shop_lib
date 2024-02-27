"""Contains functions to build disjunctive graphs and its variants."""

from __future__ import annotations

import itertools
import collections
import networkx as nx

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import Node, EdgeType, NodeType


class JobShopGraph(nx.DiGraph):
    """Represents a `JobShopInstance` as a graph."""

    def __init__(
        self, instance: JobShopInstance, incoming_graph_data=None, **attr
    ):
        super().__init__(incoming_graph_data, **attr)
        self.instance = instance
        self.nodes_by_type: dict[NodeType, list[Node]] = (
            collections.defaultdict(list)
        )
        self.nodes_by_machine: list[list[Node]] = [
            [] for _ in range(instance.num_machines)
        ]
        self.nodes_by_job: list[list[Node]] = [
            [] for _ in range(instance.num_jobs)
        ]
        self._next_node_id = 0

        self._add_operation_nodes()

    @classmethod
    def build_disjunctive_graph(
        cls, instance: JobShopInstance
    ) -> JobShopGraph:
        """Creates a disjunctive graph from a `JobShopInstance`.

        Args:
            instance (JobShopInstance): The instance to represent as a graph.

        Returns:
            JobShopGraph: The disjunctive graph of the instance.
        """
        graph = cls(instance)
        graph.add_disjunctive_edges()
        graph.add_conjunctive_edges()
        graph.add_source_sink_nodes()
        graph.add_source_sink_edges()
        return graph

    def _add_operation_nodes(self) -> None:
        """Adds operation nodes to the graph."""
        for job in self.instance.jobs:
            for operation in job:
                node = Node(node_type=NodeType.OPERATION, value=operation)
                self.add_node(node)

    def add_disjunctive_edges(self) -> None:
        """Adds disjunctive edges to the graph."""

        for machine in self.nodes_by_machine:
            for node1, node2 in itertools.combinations(machine, 2):
                self.add_edge(
                    node1,
                    node2,
                    type=EdgeType.DISJUNCTIVE,
                )
                self.add_edge(
                    node2,
                    node1,
                    type=EdgeType.DISJUNCTIVE,
                )

    def add_conjunctive_edges(self) -> None:
        """Adds conjunctive edges to the graph."""
        for job in self.nodes_by_job:
            for i in range(1, len(job)):
                self.add_edge(job[i - 1], job[i], type=EdgeType.CONJUNCTIVE)

    def add_source_sink_nodes(self) -> None:
        """Adds source and sink nodes to the graph."""
        source = Node(node_type=NodeType.SOURCE)
        sink = Node(node_type=NodeType.SINK)
        self.add_node(source)
        self.add_node(sink)

    def add_source_sink_edges(self) -> None:
        """Adds edges between source and sink nodes and operations."""
        source = self.nodes_by_type[NodeType.SOURCE][0]
        sink = self.nodes_by_type[NodeType.SINK][0]

        for job in self.nodes_by_job:
            self.add_edge(source, job[0], type=EdgeType.CONJUNCTIVE)
            self.add_edge(job[-1], sink, type=EdgeType.CONJUNCTIVE)

    def add_node(self, node_for_adding: Node, **attr) -> None:
        """Adds a node to the graph.

        Overrides the `add_node` method of the `DiGraph` class. This method
        assigns automatically an id to the node and adds it to the
        `nodes_by_type` dictionary.

        Args:
            node_for_adding (Node): The node to add to the graph.
            **attr: Any other additional attributes that are not part of the
                `Node` class interface.
        """
        node_for_adding.node_id = self._next_node_id
        super().add_node(node_for_adding, **attr)
        self.nodes_by_type[node_for_adding.node_type].append(node_for_adding)
        self._next_node_id += 1

        if node_for_adding.node_type != NodeType.OPERATION:
            return
        operation = node_for_adding.operation
        self.nodes_by_job[operation.job_id].append(node_for_adding)
        for machine_id in operation.machines:
            self.nodes_by_machine[machine_id].append(node_for_adding)
