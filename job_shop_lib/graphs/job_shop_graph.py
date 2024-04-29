"""Home of the `JobShopGraph` class."""

import collections
import networkx as nx

from job_shop_lib import JobShopInstance, JobShopLibError
from job_shop_lib.graphs import Node, NodeType


NODE_ATTR = "node"


# pylint: disable=too-many-instance-attributes
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
    """

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

        self._nodes: list[Node] = []
        self._nodes_by_type: dict[NodeType, list[Node]] = (
            collections.defaultdict(list)
        )
        self._nodes_by_machine: list[list[Node]] = [
            [] for _ in range(instance.num_machines)
        ]
        self._nodes_by_job: list[list[Node]] = [
            [] for _ in range(instance.num_jobs)
        ]
        self._next_node_id = 0
        self.removed_nodes: list[bool] = []
        self._add_operation_nodes()

    @property
    def nodes(self) -> list[Node]:
        """List of all nodes added to the graph.

        It may contain nodes that have been removed from the graph.
        """
        return self._nodes

    @property
    def nodes_by_type(self) -> dict[NodeType, list[Node]]:
        """Dictionary mapping node types to lists of nodes.

        It may contain nodes that have been removed from the graph.
        """
        return self._nodes_by_type

    @property
    def nodes_by_machine(self) -> list[list[Node]]:
        """List of lists mapping machine ids to operation nodes.

        It may contain nodes that have been removed from the graph.
        """
        return self._nodes_by_machine

    @property
    def nodes_by_job(self) -> list[list[Node]]:
        """List of lists mapping job ids to operation nodes.

        It may contain nodes that have been removed from the graph.
        """
        return self._nodes_by_job

    @property
    def num_edges(self) -> int:
        """Number of edges in the graph."""
        return self.graph.number_of_edges()

    @property
    def num_job_nodes(self) -> int:
        """Number of job nodes in the graph."""
        return len(self._nodes_by_type[NodeType.JOB])

    def _add_operation_nodes(self) -> None:
        """Adds operation nodes to the graph."""
        for job in self.instance.jobs:
            for operation in job:
                node = Node(node_type=NodeType.OPERATION, operation=operation)
                self.add_node(node)

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
        self._nodes_by_type[node_for_adding.node_type].append(node_for_adding)
        self._nodes.append(node_for_adding)
        self._next_node_id += 1
        self.removed_nodes.append(False)

        if node_for_adding.node_type == NodeType.OPERATION:
            operation = node_for_adding.operation
            self._nodes_by_job[operation.job_id].append(node_for_adding)
            for machine_id in operation.machines:
                self._nodes_by_machine[machine_id].append(node_for_adding)

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
            JobShopLibError: If `u_of_edge` or `v_of_edge` are not in the
                graph.
        """
        if isinstance(u_of_edge, Node):
            u_of_edge = u_of_edge.node_id
        if isinstance(v_of_edge, Node):
            v_of_edge = v_of_edge.node_id
        if u_of_edge not in self.graph or v_of_edge not in self.graph:
            raise JobShopLibError(
                "`u_of_edge` and `v_of_edge` must be in the graph."
            )
        self.graph.add_edge(u_of_edge, v_of_edge, **attr)

    def remove_node(self, node_id: int) -> None:
        """Removes a node from the graph and the isolated nodes that result
        from the removal.

        Args:
            node_id: The id of the node to remove.
        """
        self.graph.remove_node(node_id)
        self.removed_nodes[node_id] = True

        isolated_nodes = list(nx.isolates(self.graph))
        for isolated_node in isolated_nodes:
            self.removed_nodes[isolated_node] = True

        self.graph.remove_nodes_from(isolated_nodes)

    def is_removed(self, node: int | Node) -> bool:
        """Returns whether the node is removed from the graph.

        Args:
            node: The node to check. If it is a `Node`, its `node_id` is used
                as the node to check. Otherwise, it is assumed to be the
                `node_id` of the node to check.
        """
        if isinstance(node, Node):
            node = node.node_id
        return self.removed_nodes[node]
