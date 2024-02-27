from typing import TypeVar

from job_shop_lib.graphs.constants import NodeType

_T = TypeVar("_T")


class Node:
    __slots__ = "_node_type", "_value", "_node_id"

    def __init__(self, node_type: NodeType, value: _T = None):
        self._node_type = node_type
        self._value = value
        self._node_id = None

    @property
    def node_type(self) -> NodeType:
        return self._node_type

    @property
    def value(self) -> _T:
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
        if self._node_id is None:
            raise ValueError("Node has not been assigned an id.")
        return hash(self._node_id)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Node):
            return False
        return self.node_id == __value.node_id

    def __repr__(self) -> str:
        return (
            f"Node(node_type={self.node_type}, value={self.value}, "
            f"id={self._node_id})"
        )
