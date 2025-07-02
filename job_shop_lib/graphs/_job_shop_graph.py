"""Home of the `JobShopGraph` class."""

import collections
import networkx as nx

from job_shop_lib import JobShopInstance
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.graphs import Node, NodeType


NODE_ATTR = "node"


# pylint: disable=too-many-instance-attributes
class JobShopGraph:
    """Represents a :class:`JobShopInstance` as a heterogeneous directed graph.

    Provides a comprehensive graph-based representation of a job shop
    scheduling problem, utilizing the ``networkx`` library to model the complex
    relationships between jobs, operations, and machines. This class transforms
    the abstract scheduling problem into a directed graph, where various
    entities (jobs, machines, and operations) are nodes, and the dependencies
    (such as operation order within a job or machine assignment) are edges.

    This transformation allows for the application of graph algorithms
    to analyze and solve scheduling problems.

    The class now generates and manages node identifiers as tuples of the
    form `(node_type_name, local_id)`, e.g., `("OPERATION", 42)`.

    Args:
        instance:
            The job shop instance that the graph represents.
        add_operation_nodes:
            Whether to add nodes of type :class:`NodeType.OPERATION` to the
            to the graph. If set to ``False``, the graph will be empty, and
            operation nodes will need to be added manually.
    """

    __slots__ = {
        "instance": "The job shop instance that the graph represents.",
        "_nodes": "List of all nodes added to the graph.",
        "_nodes_map": "Dictionary mapping node tuple ids to Node objects.",
        "_nodes_by_type": "Dictionary mapping node types to lists of nodes.",
        "_nodes_by_machine": (
            "List of lists mapping machine ids to operation nodes."
        ),
        "_nodes_by_job": "List of lists mapping job ids to operation nodes.",
        "_next_node_id": (
            "Dictionary mapping node types to their next available local id."
        ),
        "removed_nodes": (
            "Dictionary mapping node types to a list of boolean values "
            "indicating whether a node has been removed from the graph."
        ),
        "edge_index_dict": (
            "Stores graph connectivity, keyed by ('source', 'to', 'dest')."
        ),
    }

    def __init__(
        self, instance: JobShopInstance, add_operation_nodes: bool = True
    ):
        self.instance = instance

        self._nodes: list[Node] = []
        self._nodes_map: dict[tuple[str, int], Node] = {}
        self._nodes_by_type: dict[NodeType, list[Node]] = (
            collections.defaultdict(list)
        )
        self._nodes_by_machine: list[list[Node]] = [
            [] for _ in range(instance.num_machines)
        ]
        self._nodes_by_job: list[list[Node]] = [
            [] for _ in range(instance.num_jobs)
        ]
        # Changed: _next_node_id is now a dictionary
        self._next_node_id = collections.defaultdict(int)
        # Changed: removed_nodes is now a dictionary of lists
        self.removed_nodes: dict[str, list[bool]] = collections.defaultdict(
            list
        )
        self.edge_index_dict: dict[
            tuple[str, str, str], list[tuple[str, int] | Node]
        ] = collections.defaultdict(list)

        if add_operation_nodes:
            self.add_operation_nodes()

    @property
    def graph(self) -> nx.DiGraph:
        """Constructs and returns a networkx.DiGraph object on-demand.

        The generated graph respects all node removals, containing only the
        active nodes and the edges between them.
        """
        g = nx.DiGraph()
        # Add only the nodes that have not been removed
        for node_id, node_obj in self._nodes_map.items():
            if not self.is_removed(node_id):
                g.add_node(node_id, **{NODE_ATTR: node_obj})

        # Add edges, ensuring both endpoints are active nodes
        for edge_type, edge_list in self.edge_index_dict.items():
            for u, v in edge_list:
                if not self.is_removed(u) and not self.is_removed(v):
                    g.add_edge(u.node_id, v.node_id, type=edge_type)
        return g
    
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
        return sum(len(edges) for edges in self.edge_index_dict.values())

    @property
    def num_job_nodes(self) -> int:
        """Number of job nodes in the graph."""
        return len(self._nodes_by_type[NodeType.JOB])

    def add_operation_nodes(self) -> None:
        """Adds operation nodes to the graph."""
        for job in self.instance.jobs:
            for operation in job:
                node = Node(node_type=NodeType.OPERATION, operation=operation)
                self.add_node(node)

    def add_node(self, node_for_adding: Node) -> None:
        """Adds a node to the graph and updates relevant class attributes.

        This method assigns a unique identifier to the node, adds it to the
        graph, and updates the nodes list and the nodes_by_type dictionary. The
        id is a tuple `(node_type_name, local_id)`. If the node is of type
        :class:`NodeType.OPERATION`, it also updates ``nodes_by_job`` and
        ``nodes_by_machine`` based on the operation's job id and machine ids.

        Args:
            node_for_adding:
                The node to be added to the graph.

        Note:
            This method directly modifies the graph attribute as well as
            several other class attributes. Thus, adding nodes to the graph
            should be done exclusively through this method to avoid
            inconsistencies.
        """
        # Changed: Node ID generation logic
        node_type_name = node_for_adding.node_type.name
        local_id = self._next_node_id[node_type_name]
        new_id = (node_type_name, local_id)

        node_for_adding.node_id = new_id
        self._nodes_by_type[node_for_adding.node_type].append(node_for_adding)
        self._nodes.append(node_for_adding)
        self._nodes_map[new_id] = node_for_adding
        self._next_node_id[node_type_name] += 1
        self.removed_nodes[node_type_name].append(False)

        if node_for_adding.node_type == NodeType.OPERATION:
            operation = node_for_adding.operation
            self._nodes_by_job[operation.job_id].append(node_for_adding)
            for machine_id in operation.machines:
                self._nodes_by_machine[machine_id].append(node_for_adding)

    def add_edge(
        self,
        u_of_edge: Node | tuple[str, int],
        v_of_edge: Node | tuple[str, int],
        **attr,
    ) -> None:
        """Adds an edge to the graph.

        It automatically determines the edge type based on the source and
        destination nodes unless explicitly provided in the ``attr`` argument
        via the ``type`` key. The edge type is a tuple of strings:
        ``(source_node_type, "to", destination_node_type)``.

        Args:
            u_of_edge:
                The source node of the edge. Can be a :class:`Node` or
                its tuple id.
            v_of_edge:
                The destination node of the edge. Can be a :class:`Node` or
                its tuple id.
            **attr:
                Additional attributes to be added to the edge.

        Raises:
            ValidationError: If ``u_of_edge`` or ``v_of_edge`` are not in the
                graph.
        """
        if isinstance(u_of_edge, tuple):
            u_of_edge = self._nodes_map.get((u_of_edge[0], u_of_edge[1]))
        if isinstance(v_of_edge, tuple):
            v_of_edge = self._nodes_map.get((v_of_edge[0], v_of_edge[1]))
        if u_of_edge is None or v_of_edge is None:
            raise ValidationError(
                "`u_of_edge` and `v_of_edge` must have been added to the graph."
            )
        edge_type = attr.pop("type", None)
        if edge_type is None:
            edge_type = (
                u_of_edge.node_id[0],
                "to",
                v_of_edge.node_id[0]
            )
        self.edge_index_dict[edge_type].append((u_of_edge, v_of_edge))

    def remove_node(self, node_id: tuple[str, int]) -> None:
        """Marks a node as removed and deletes all edges connected to it.

        This operation can be slow if the graph is large, as it rebuilds
        the entire edge dictionary.
        """
        # First, flag the node as removed so it's consistently marked
        node_type_name, local_id = node_id
        if local_id < len(self.removed_nodes[node_type_name]):
            self.removed_nodes[node_type_name][local_id] = True
        else:
            return  # Node doesn't exist, nothing to do
    
        # Remove all edges connected to the node
        for edge_type, edge_list in self.edge_index_dict.items():
            # Only check lists where the node type could possibly appear
            if not isinstance(edge_type, tuple):
                self.edge_index_dict[edge_type] = [
                    (u, v) for u, v in edge_list if u != node_id and v != node_id
                ]
            else:
                if node_type_name in (edge_type[0], edge_type[2]):
                    self.edge_index_dict[edge_type] = [
                        (u, v) for u, v in edge_list if u != node_id and v != node_id
                    ]
                    
    def remove_isolated_nodes(self) -> None:
        """Removes isolated nodes from the graph."""
        active_nodes = {node.node_id for node in self.non_removed_nodes()}
        nodes_with_edges = set()
        for edge_list in self.edge_index_dict.values():
            for u, v in edge_list:
                nodes_with_edges.add(u.node_id if isinstance(u, Node) else u)
                nodes_with_edges.add(v.node_id if isinstance(v, Node) else v)
        isolated_node_ids = active_nodes - nodes_with_edges
        for node_id in isolated_node_ids:
            node_type_name, local_id = node_id
            if local_id < len(self.removed_nodes[node_type_name]):
                self.removed_nodes[node_type_name][local_id] = True

    def is_removed(self, node: tuple[str, int] | Node) -> bool:
        """Returns whether the node is removed from the graph.

        Args:
            node:
                The node to check. Can be a :class:`Node` or its tuple id.
        """
        if isinstance(node, Node):
            node_id = node.node_id
        else:
            node_id = node

        # Changed: Check removed_nodes dictionary
        node_type_name, local_id = node_id
        type_removed_list = self.removed_nodes[node_type_name]

        if local_id >= len(type_removed_list):
            return False  # Node was never added or list is out of sync

        return type_removed_list[local_id]

    def non_removed_nodes(self) -> list[Node]:
        """Returns the nodes that are not removed from the graph."""
        return [node for node in self._nodes if not self.is_removed(node)]

    def get_machine_node(self, machine_id: int) -> Node:
        """Returns the node representing the machine with the given id.

        Args:
            machine_id: The id of the machine.

        Returns:
            The node representing the machine with the given id.
        """
        return self.get_node_by_type_and_id(
            NodeType.MACHINE, machine_id, "machine_id"
        )

    def get_job_node(self, job_id: int) -> Node:
        """Returns the node representing the job with the given id.

        Args:
            job_id: The id of the job.

        Returns:
            The node representing the job with the given id.
        """
        return self.get_node_by_type_and_id(NodeType.JOB, job_id, "job_id")

    def get_operation_node(self, operation_id: int) -> Node:
        """Returns the node representing the operation with the given id.

        Args:
            operation_id: The id of the operation.

        Returns:
            The node representing the operation with the given id.
        """
        return self.get_node_by_type_and_id(
            NodeType.OPERATION, operation_id, "operation.operation_id"
        )

    def get_node_by_type_and_id(
        self, node_type: NodeType, node_id: int, id_attr: str
    ) -> Node:
        """Generic method to get a node by type and id.

        Args:
            node_type:
                The type of the node.
            node_id:
                The id of the node.
            id_attr:
                The attribute name to compare the id. Can be nested like
                'operation.operation_id'.

        Returns:
            The node with the given id.
        """

        def get_nested_attr(obj, attr_path: str):
            """Helper function to get nested attribute."""
            attrs = attr_path.split(".")
            for attr in attrs:
                obj = getattr(obj, attr)
            return obj

        nodes = self._nodes_by_type[node_type]
        if node_id < len(nodes):
            node = nodes[node_id]
            if get_nested_attr(node, id_attr) == node_id:
                return node

        for node in nodes:
            if get_nested_attr(node, id_attr) == node_id:
                return node

        raise ValidationError(f"No node found with node.{id_attr}={node_id}")
