"""Home of the `JobShopGraph` class."""

import collections
import networkx as nx

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.graphs import Node, NodeType


NODE_ATTR = "node"


class JobShopGraph:
    """Data structure to represent a `JobShopInstance` as a graph.

    Provides a comprehensive graph-based representation of a job shop
    scheduling problem, utilizing the `networkx` library to model the complex
    relationships between jobs, operations, and machines. This class transforms
    the abstract scheduling problem into a directed graph, where various
    entities (jobs, machines, and operations) are nodes, and the dependencies
    (such as operation order within a job or machine assignment) are edges.

    This transformation allows for the application of graph algorithms
    to analyze and solve scheduling problems.

    Attributes:
        instance:
            The job shop instance encapsulated by this graph.
        graph:
            The directed graph representing the job shop, where nodes are
                operations, machines, jobs, or abstract concepts like global,
                source, and sink, with edges indicating dependencies.
        nodes:
            A list of all nodes, encapsulated by the `Node` class, in the
                graph.
        nodes_by_type:
            A dictionary categorizing nodes by their `NodeType`,
                facilitating access to nodes of a particular type.
        nodes_by_machine:
            A nested list mapping each machine to its associated
                operation nodes, aiding in machine-specific analysis.
        nodes_by_job:
            Similar to `nodes_by_machine`, but maps jobs to their
                operation nodes, useful for job-specific traversal.
    """

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
        """Initializes the graph with the given instance.

        Nodes of type `OPERATION` are added to the graph based on the
        operations of the instance.

        Args:
            instance:
                The job shop instance that the graph represents.
        """
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
                node = Node(node_type=NodeType.OPERATION, operation=operation)
                self.add_node(node)

    def get_operation_from_id(self, operation_id: int) -> Operation:
        """Returns the operation with the given id."""
        return self.nodes[operation_id].operation

    def add_node(self, node_for_adding: Node) -> None:
        """Adds a node to the graph and updates relevant class attributes.

        This method assigns a unique identifier to the node, adds it to the
        graph, and updates the nodes list and the nodes_by_type dictionary. If
        the node is of type `OPERATION`, it also updates `nodes_by_job` and
        `nodes_by_machine` based on the operation's job_id and machine_ids.

        Args:
            node_for_adding (Node): The node to be added to the graph.

        Raises:
            ValueError: If the node type is unsupported or if required
            attributes for the node type are missing.

        Note:
            This method directly modifies the graph attribute as well as
            several other class attributes. Thus, adding nodes to the graph
            should be done exclusively through this method to avoid
            inconsistencies.
        """
        node_for_adding.node_id = self._next_node_id
        self.graph.add_node(
            node_for_adding.node_id, **{NODE_ATTR: node_for_adding}
        )
        self.nodes_by_type[node_for_adding.node_type].append(node_for_adding)
        self.nodes.append(node_for_adding)
        self._next_node_id += 1

        if node_for_adding.node_type == NodeType.OPERATION:
            operation = node_for_adding.operation
            self.nodes_by_job[operation.job_id].append(node_for_adding)
            for machine_id in operation.machines:
                self.nodes_by_machine[machine_id].append(node_for_adding)

    def add_edge(
        self, u_of_edge: Node | int, v_of_edge: Node | int, **attr
    ) -> None:
        """Adds an edge to the graph.

        Args:
            u_of_edge: The source node of the edge. If it is a `Node`, its
                `node_id` is used as the source. Otherwise, it is assumed to be
                the node_id of the source.
            v_of_edge: The destination node of the edge. If it is a `Node`, its
                `node_id` is used as the destination. Otherwise, it is assumed
                to be the node_id of the destination.
            **attr: Additional attributes to be added to the edge.

        Raises:
            ValueError: If `u_of_edge` or `v_of_edge` are not in the graph.
        """
        if isinstance(u_of_edge, Node):
            u_of_edge = u_of_edge.node_id
        if isinstance(v_of_edge, Node):
            v_of_edge = v_of_edge.node_id
        if u_of_edge not in self.graph or v_of_edge not in self.graph:
            raise ValueError(
                "`u_of_edge` and `v_of_edge` must be in the graph."
            )
        self.graph.add_edge(u_of_edge, v_of_edge, **attr)
