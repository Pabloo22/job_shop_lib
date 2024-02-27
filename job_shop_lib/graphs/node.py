from typing import Optional, Any

from job_shop_lib import Operation
from job_shop_lib.graphs.constants import NodeType


class Node:
    __slots__ = "_node_type", "_value", "_node_id"

    def __init__(self, node_type: NodeType, value: Any = None):
        if node_type == NodeType.OPERATION and not isinstance(
            value, Operation
        ):
            raise ValueError(
                "value must be an Operation for NodeType.OPERATION"
            )

        self._node_type = node_type
        self._value = value
        self._node_id: Optional[int] = None

    @property
    def node_type(self) -> NodeType:
        return self._node_type

    @property
    def value(self) -> Any:
        return self._value

    @property
    def operation(self) -> Operation:
        if not isinstance(self._value, Operation):
            raise ValueError("Node does not have an operation.")
        return self._value

    @property
    def node_id(self) -> int:
        if self._node_id is None:
            raise ValueError("Node has not been assigned an id.")
        return self._node_id

    @node_id.setter
    def node_id(self, value: int) -> None:
        if self._node_id is not None:
            raise ValueError("node_id can only be modified once.")
        self._node_id = value

    def __hash__(self) -> int:
        return hash(self.node_id)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Node):
            return False
        return self.node_id == __value.node_id

    def __repr__(self) -> str:
        return (
            f"Node(node_type={self.node_type.name}, value={self.value}, "
            f"id={self._node_id})"
        )
