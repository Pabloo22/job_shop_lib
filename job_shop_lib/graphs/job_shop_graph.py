"""Contains functions to build disjunctive graphs and its variants."""

import collections
import networkx as nx

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import Node, NodeType


NODE_ATTR = "node"


class JobShopGraph:
    """Represents a `JobShopInstance` as a graph."""

    __slots__ = (
        "instance",
        "graph",
        "nodes",
        "nodes_by_type",
        "nodes_by_machine",
        "nodes_by_job",
        "_next_node_id",
    )

    def __init__(self, instance: JobShopInstance):
        self.graph = nx.DiGraph()
        self.instance = instance

        self.nodes: list[Node] = []

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
                node = Node.create_node_with_data(
                    node_type=NodeType.OPERATION, data=operation
                )
                self.add_node(node)

    def add_node(self, node_for_adding: Node) -> None:
        """Adds a node to the graph.

        Note:
            Don't modify self.graph directly. Use this method instead.

        Args:
            node_for_adding (Node): The node to add to the graph.
            **attr: Any other additional attributes that are not part of the
                `Node` class interface.
        """
        node_for_adding.node_id = self._next_node_id
        self.graph.add_node(self._next_node_id, **{NODE_ATTR: node_for_adding})
        self.nodes_by_type[node_for_adding.node_type].append(node_for_adding)
        self.nodes.append(node_for_adding)
        self._next_node_id += 1

        if node_for_adding.node_type != NodeType.OPERATION:
            return
        operation = node_for_adding.operation
        self.nodes_by_job[operation.job_id].append(node_for_adding)
        for machine_id in operation.machines:
            self.nodes_by_machine[machine_id].append(node_for_adding)

    def add_edge(
        self, u_of_edge: Node | int, v_of_edge: Node | int, **attr
    ) -> None:
        """Adds an edge to the graph.

        Note:
            Don't modify self.graph directly. Use this method instead.

        Args:
            u_of_edge (Node): The source node of the edge.
            v_of_edge (Node): The destination node of the edge.
            **attr: Any other additional attributes that are not part of the
                `Edge` class interface.
        """
        u_of_edge = (
            u_of_edge.node_id if isinstance(u_of_edge, Node) else u_of_edge
        )
        v_of_edge = (
            v_of_edge.node_id if isinstance(v_of_edge, Node) else v_of_edge
        )
        if u_of_edge not in self.graph or v_of_edge not in self.graph:
            raise ValueError("u_of_edge and v_of_edge must be in the graph.")
        self.graph.add_edge(u_of_edge, v_of_edge, **attr)
