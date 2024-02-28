"""Contains functions to build disjunctive graphs and its variants."""

from __future__ import annotations

import collections
import networkx as nx

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import Node, NodeType


class JobShopGraph(nx.DiGraph):
    """Represents a `JobShopInstance` as a graph."""

    __slots__ = (
        "instance",
        "nodes_by_type",
        "nodes_by_machine",
        "nodes_by_job",
        "_next_node_id",
    )

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

    def _add_operation_nodes(self) -> None:
        """Adds operation nodes to the graph."""
        for job in self.instance.jobs:
            for operation in job:
                node = Node(node_type=NodeType.OPERATION, value=operation)
                self.add_node(node)

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
