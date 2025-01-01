"""Home of the `Node` class."""

from typing import Optional

from job_shop_lib import Operation
from job_shop_lib.exceptions import (
    UninitializedAttributeError,
    ValidationError,
)
from job_shop_lib.graphs._constants import NodeType


class Node:
    """Represents a node in the :class:`JobShopGraph`.

    A node is hashable by its id. The id is assigned when the node is added to
    the graph. The id must be unique for each node in the graph, and should be
    used to identify the node in the networkx graph.

    Depending on the type of the node, it can have different attributes. The
    following table shows the attributes of each type of node:

    +----------------+---------------------+
    | Node Type      | Required Attribute  |
    +================+=====================+
    | OPERATION      | ``operation``       |
    +----------------+---------------------+
    | MACHINE        | ``machine_id``      |
    +----------------+---------------------+
    | JOB            | ``job_id``          |
    +----------------+---------------------+

    In terms of equality, two nodes are equal if they have the same id.
    Additionally, one node is equal to an integer if the integer is equal to
    its id. It is also hashable by its id.

    This allows for using the node as a key in a dictionary, at the same time
    we can use its id to index that dictionary. Example:

    .. code-block:: python

        node = Node(NodeType.SOURCE)
        node.node_id = 1
        graph = {node: "some value"}
        print(graph[node])  # "some value"
        print(graph[1])  # "some value"

    Args:
        node_type:
            The type of the node. See :class:`NodeType` for theavailable types.
        operation:
            The operation of the node. Required if ``node_type`` is
            :attr:`NodeType.OPERATION`.
        machine_id:
            The id of the machine. Required if ``node_type`` is
            :attr:`NodeType.MACHINE`.
        job_id:
            The id of the job. Required if ``node_type`` is
            :attr:`NodeType.JOB`.

    Raises:
        ValidationError:
            If the ``node_type`` is :attr:`NodeType.OPERATION`,
            :attr:`NodeType.MACHINE`, or :attr:`NodeType.JOB` and the
            corresponding ``operation``, ``machine_id``, or ``job_id`` is
            ``None``, respectively.

    """

    __slots__ = {
        "node_type": "The type of the node.",
        "_node_id": "Unique identifier for the node.",
        "_operation": (
            "The operation associated with the node."
        ),
        "_machine_id": (
            "The machine ID associated with the node."
        ),
        "_job_id": "The job ID associated with the node.",
    }

    def __init__(
        self,
        node_type: NodeType,
        operation: Optional[Operation] = None,
        machine_id: Optional[int] = None,
        job_id: Optional[int] = None,
    ):
        if node_type == NodeType.OPERATION and operation is None:
            raise ValidationError("Operation node must have an operation.")

        if node_type == NodeType.MACHINE and machine_id is None:
            raise ValidationError("Machine node must have a machine_id.")

        if node_type == NodeType.JOB and job_id is None:
            raise ValidationError("Job node must have a job_id.")

        self.node_type: NodeType = node_type
        self._node_id: Optional[int] = None

        self._operation = operation
        self._machine_id = machine_id
        self._job_id = job_id

    @property
    def node_id(self) -> int:
        """Returns a unique identifier for the node."""
        if self._node_id is None:
            raise UninitializedAttributeError(
                "Node has not been assigned an id."
            )
        return self._node_id

    @node_id.setter
    def node_id(self, value: int) -> None:
        self._node_id = value

    @property
    def operation(self) -> Operation:
        """Returns the operation of the node.

        This property is mandatory for nodes of type
        :class:`NodeType.OPERATION`.

        Raises:
            UninitializedAttributeError: If the node has no operation.
        """
        if self._operation is None:
            raise UninitializedAttributeError("Node has no operation.")
        return self._operation

    @property
    def machine_id(self) -> int:
        """Returns the `machine_id` of the node.

        This property is mandatory for nodes of type `MACHINE`.

        Raises:
            UninitializedAttributeError: If the node has no ``machine_id``.
        """
        if self._machine_id is None:
            raise UninitializedAttributeError("Node has no ``machine_id``.")
        return self._machine_id

    @property
    def job_id(self) -> int:
        """Returns the `job_id` of the node.

        This property is mandatory for nodes of type `JOB`.

        Raises:
            UninitializedAttributeError: If the node has no `job_id`.
        """
        if self._job_id is None:
            raise UninitializedAttributeError("Node has no `job_id`.")
        return self._job_id

    def __hash__(self) -> int:
        return self.node_id

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Node):
            __value = __value.node_id
        return self.node_id == __value

    def __repr__(self) -> str:
        if self.node_type == NodeType.OPERATION:
            return (
                f"Node(node_type={self.node_type.name}, id={self._node_id}, "
                f"operation={self.operation})"
            )
        if self.node_type == NodeType.MACHINE:
            return (
                f"Node(node_type={self.node_type.name}, id={self._node_id}, "
                f"machine_id={self._machine_id})"
            )
        if self.node_type == NodeType.JOB:
            return (
                f"Node(node_type={self.node_type.name}, id={self._node_id}, "
                f"job_id={self._job_id})"
            )
        return f"Node(node_type={self.node_type.name}, id={self._node_id})"
